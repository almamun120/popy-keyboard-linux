"""Fixed keyboard layouts (.avrolayout, format v5) and the typing logic.

Port of Delphi clsGenericLayoutModern.pas.  Instead of back-spacing in the
target application, the word being typed is kept in a buffer (shown as IBus
preedit text), so reordering (reph, kar fixing) is trivial and works in every
application.

Public API
----------
load_layout(path) -> FixedLayout
list_layouts(dirs) -> [FixedLayout, ...]      (sorted by name; no images decoded)
FixedLayout: name, version, developer, comment, path, image_normal(), image_altgr()
             (raw BMP bytes or None), char_for(key_name, shift, altgr) -> str
key_name_for_evdev(code) -> 'A' / '1' / 'OEM1' / 'NumAdd' ...
LayoutSession(layout, settings): key(evdev, shift, caps, altgr) -> Result
    Result.handled: key consumed (buffer changed);  False -> pass the key through
    Result.commit : text that must be committed *before* handling (word finished)
    session.buffer : current word (Unicode) shown as preedit;  session.reset()
"""
import base64
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

HASANTA = "্"; ZWJ = "‍"; ZWNJ = "‌"
R = "র"; Z = "য"; CHANDRA = "ঁ"

# independent vowel for each kar
KAR_TO_VOWEL = {"া": "আ", "ি": "ই", "ী": "ঈ", "ু": "উ",
                "ূ": "ঊ", "ৃ": "ঋ", "ে": "এ", "ৈ": "ঐ",
                "ো": "ও", "ৌ": "ঔ"}
KARS = set(KAR_TO_VOWEL) | {"ৄ", "ৢ", "ৣ"}
PURE_CONS = set(chr(c) for c in range(0x0995, 0x09ba)) | {"ড়", "ঢ়", "য়", "ৎ", "ৰ", "ৱ"}

_DEAD = set("`~!@#$%^+*-_=+\\|\"/;:,./?><()[]{}'1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM")
_DEAD |= set("০১২৩৪৫৬৭৮৯")
_DEAD |= set("অআইঈউঊঋএঐওঔ") | KARS | set("ংঃৎ।৳ৗ৲")
_DEAD |= {"ঌ", "ৡ", "ৠ"}

# evdev keycode -> key name used in .avrolayout (Key_<name>_<Mod>)
EVDEV = {}
for i, ch in enumerate("1234567890"):
    EVDEV[2 + i] = ch
EVDEV[12] = "MINUS"; EVDEV[13] = "PLUS"
for i, ch in enumerate("QWERTYUIOP"):
    EVDEV[16 + i] = ch
EVDEV[26] = "OEM4"; EVDEV[27] = "OEM6"
for i, ch in enumerate("ASDFGHJKL"):
    EVDEV[30 + i] = ch
EVDEV[39] = "OEM1"; EVDEV[40] = "OEM7"; EVDEV[41] = "OEM3"; EVDEV[43] = "OEM5"
for i, ch in enumerate("ZXCVBNM"):
    EVDEV[44 + i] = ch
EVDEV[51] = "COMMA"; EVDEV[52] = "PERIOD"; EVDEV[53] = "OEM2"
EVDEV.update({55: "NumMultiply", 74: "NumSubtract", 78: "NumAdd", 83: "NumDecimal", 98: "NumDivide",
              71: "Num7", 72: "Num8", 73: "Num9", 75: "Num4", 76: "Num5", 77: "Num6",
              79: "Num1", 80: "Num2", 81: "Num3", 82: "Num0"})
LETTER_KEYS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def key_name_for_evdev(code):
    return EVDEV.get(code)


@dataclass
class Settings:
    vowel_formatting: bool = True
    old_style_reph: bool = True
    fix_chandra: bool = True


class FixedLayout:
    def __init__(self, path):
        self.path = path
        raw = open(path, encoding="utf-8-sig").read()
        root = ET.fromstring(raw.lstrip("﻿").encode("utf-8"))
        g = lambda t: (root.findtext(t) or "").strip()
        self.name = g("LayoutName")
        self.version = g("LayoutVersion")
        self.developer = g("DeveloperName")
        self.comment = (root.findtext("DeveloperComment") or "").strip()
        self._img = {"normal": g("ImageNormalShift"), "altgr": g("ImageAltGrShift")}
        self.keys = {}
        kd = root.find("KeyData")
        for el in (kd if kd is not None else []):
            self.keys[el.tag] = (el.text or "").strip()

    def _image(self, which):
        s = re.sub(r"\s+", "", self._img[which])
        return base64.b64decode(s) if s else None

    def image_normal(self):
        return self._image("normal")

    def image_altgr(self):
        return self._image("altgr")

    def char_for(self, key, shift, altgr):
        mod = ("ShiftAltGr" if shift else "AltGr") if altgr else ("Shift" if shift else "Normal")
        return self.keys.get("Key_%s_%s" % (key, mod), "")


def load_layout(path):
    return FixedLayout(path)


def list_layouts(dirs):
    seen = {}
    for d in dirs:
        try:
            import os
            for fn in sorted(os.listdir(d)):
                if fn.lower().endswith(".avrolayout"):
                    try:
                        lay = FixedLayout(os.path.join(d, fn))
                    except Exception:
                        continue
                    seen.setdefault(lay.name.lower(), lay)
        except OSError:
            pass
    return sorted(seen.values(), key=lambda l: l.name.lower())


@dataclass
class Result:
    handled: bool = False
    commit: str = ""


class LayoutSession:
    def __init__(self, layout, settings=None):
        self.layout = layout
        self.s = settings or Settings()
        self.buffer = ""
        self.dead = False

    def reset(self):
        self.buffer = ""
        self.dead = False

    # --- helpers -------------------------------------------------------
    def _last(self, n=1):
        """n-th last char of buffer (1 = last) or ' '."""
        return self.buffer[-n] if len(self.buffer) >= n else " "

    def _ibs(self, n=1):
        n = min(n, len(self.buffer))
        self.buffer = self.buffer[:len(self.buffer) - n]

    def backspace(self):
        """True if a buffered char was removed (key consumed)."""
        if not self.buffer:
            return False
        self.buffer = self.buffer[:-1]
        self.dead = False
        return True

    def _insert_reph(self):
        last = self._last
        if not self.s.old_style_reph:
            return R + HASANTA
        if last(1) in PURE_CONS:
            movable = True
        elif last(1) in KARS:
            movable = last(2) in PURE_CONS
        elif last(1) == CHANDRA:
            movable = last(2) in PURE_CONS or (last(2) in KARS and last(3) in PURE_CONS)
        else:
            movable = False
        if not movable:
            return R + HASANTA
        i = 1
        if last(1) in KARS and last(2) in PURE_CONS:
            i = 2
        elif last(1) == CHANDRA:
            if last(2) in PURE_CONS:
                i = 2
            elif last(2) in KARS and last(3) in PURE_CONS:
                i = 3
        while i < len(self.buffer) + 1:
            if last(i + 1) == HASANTA:
                if last(i + 2) in PURE_CONS:
                    i += 2
                    continue
            break
        i = min(i, len(self.buffer))
        tmp = self.buffer[len(self.buffer) - i:]
        self._ibs(i)
        return R + HASANTA + tmp

    # --- main ----------------------------------------------------------
    def key(self, evdev, shift=False, caps=False, altgr=False):
        name = key_name_for_evdev(evdev)
        if name is None:
            return Result(False)
        logical = (shift != caps) if name in LETTER_KEYS else shift
        ch = self.layout.char_for(name, logical, altgr)
        if ch == "":
            commit = self.buffer
            self.reset()
            return Result(False, commit)
        if not self.s.vowel_formatting:
            self.dead = False
        out = self._process(ch)
        if out is None:
            return Result(False)
        return Result(True)

    def _process(self, ch):
        if self.dead:
            if ch in KAR_TO_VOWEL:
                self.buffer += KAR_TO_VOWEL[ch]
                return True
            self.dead = False
        if self._last() == HASANTA:
            if ch in KAR_TO_VOWEL:
                self._ibs()
                self.buffer += KAR_TO_VOWEL[ch]
                self.dead = True
                return True
            if ch == HASANTA:
                self.buffer += ZWNJ
                self.dead = True
                return True
        if ch == R + HASANTA:
            self.buffer = self.buffer + ""  # reph may rewrite the buffer
            res = self._insert_reph()
            self.buffer += res
            return True
        if ch == HASANTA + Z:
            if self._last() == R and self._last(2) != HASANTA:
                self.buffer += ZWJ + HASANTA + Z
            else:
                self.buffer += HASANTA + Z
            return True
        if ch[-1] in _DEAD:
            if ch[-1] in KARS:
                self.dead = True
                if self.s.fix_chandra and self._last() == CHANDRA:
                    self._ibs()
                    self.buffer += ch + CHANDRA
                else:
                    self.buffer += ch
            else:
                self.dead = True
                self.buffer += ch
            return True
        self.buffer += ch
        return True
