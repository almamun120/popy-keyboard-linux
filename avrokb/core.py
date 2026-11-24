"""Toolkit independent typing core used by the IBus engine (and unit tests).

Feed key events with TypingCore.process(); it returns an Action describing what the
front-end must do (commit text, show preedit, show candidates) and whether the key was consumed.
"""
import os
from dataclasses import dataclass, field

from . import avro_phonetic, bijoy, config, layouts, popy, popy_dict

# X11 keysyms
K_SPACE = 0x20; K_BACKSPACE = 0xFF08; K_TAB = 0xFF09; K_RETURN = 0xFF0D; K_KP_ENTER = 0xFF8D
K_ESCAPE = 0xFF1B; K_UP = 0xFF52; K_DOWN = 0xFF54; K_LEFT = 0xFF51; K_RIGHT = 0xFF53
K_HOME = 0xFF50; K_END = 0xFF57; K_DELETE = 0xFFFF; K_PGUP = 0xFF55; K_PGDN = 0xFF56
K_F12 = 0xFFC9; K_SUPER_R = 0xFFEC; K_CONTROL_R = 0xFFE4; K_SHIFT_L = 0xFFE1; K_SHIFT_R = 0xFFE2
K_CONTROL_L = 0xFFE3

MODIFIER_KEYSYMS = set(range(0xFFE1, 0xFFEF)) | {0xFE03}


@dataclass
class Mods:
    shift: bool = False
    ctrl: bool = False
    alt: bool = False
    super: bool = False
    caps: bool = False
    altgr: bool = False
    release: bool = False


@dataclass
class Action:
    consumed: bool = False
    commit: str = ""
    preedit: str = ""             # shown underlined; "" hides it
    candidates: list = field(default_factory=list)
    cursor: int = -1              # selected candidate or -1
    aux: str = ""                 # preview line: the typed English letters
    mode_changed: bool = False
    update: bool = False          # key not consumed, but the preedit / preview changed (Shift tap)


class TypingCore:
    def __init__(self, settings=None, layout_dirs=None, engine_name=None):
        self.settings = dict(settings or config.load())
        self.engine_name = engine_name
        self._dirs = layout_dirs or config.layout_dirs()
        self.bangla = self.settings.get("start_mode", "bangla") != "english"
        self.buf = ""                 # latin buffer (popy / avro)
        self.session = None           # fixed layout session
        self.cands = []
        self.sel = -1
        self._toggle_pending = False
        self._shift_down = False      # a Shift key is held ...
        self._shift_tap = False       # ... and nothing else was pressed meanwhile = a tap
        self._avro = None
        popy.GREEDY = bool(self.settings.get("popy_greedy", True))
        self._load_layout()

    # ---------- configuration ----------
    def apply_settings(self, settings):
        self.settings = dict(settings)
        popy.GREEDY = bool(self.settings.get("popy_greedy", True))
        self._load_layout()

    def _load_layout(self):
        self.flush()
        if self.engine_name:
            names = [l.name for l in layouts.list_layouts(self._dirs)]
            name = config.engine_layout(self.engine_name, self.settings, names)
        else:
            name = self.settings.get("layout", "Avro Phonetic")
        self.layout_label = name
        self.kind = "avro"
        self.session = None
        if name.lower() == "popy":
            self.kind = "popy"
        elif name.lower() != "avro phonetic":
            for lay in layouts.list_layouts(self._dirs):
                if lay.name.lower() == name.lower():
                    st = layouts.Settings(self.settings.get("vowel_formatting", True),
                                          self.settings.get("old_style_reph", True),
                                          self.settings.get("fix_chandra", True))
                    self.session = layouts.LayoutSession(lay, st)
                    self.kind = "fixed"
                    break
        if self.kind == "avro":
            self._avro = avro_phonetic.EnglishToBangla(
                self.settings.get("avro_autocorrect", True), self.settings.get("jo_nukta", False),
                avro_phonetic.AutoCorrect())

    # ---------- helpers ----------
    def _out(self, text):
        return bijoy.unicode_to_bijoy(text) if self.settings.get("output_ansi") else text

    def _convert(self, latin):
        if self.kind == "popy":
            return popy.preview(latin)[0]
        return self._avro.convert(latin)

    def _popy_auto(self):
        return bool(self.settings.get("popy_autocorrect", True))

    def _final(self, latin):
        if self.kind == "popy":
            text = popy.convert(latin)
            if self._popy_auto():
                try:
                    text = popy_dict.get().correct(text)
                except Exception:
                    pass
            return text
        return self._avro.convert(latin)

    def current_text(self):
        if self.kind == "fixed":
            return self.session.buffer
        return self._convert(self.buf) if self.buf else ""

    def has_text(self):
        return bool(self.session.buffer) if self.kind == "fixed" else bool(self.buf)

    def flush(self):
        """Return text to commit for the pending word and clear all state."""
        out = ""
        if getattr(self, "session", None) is not None and self.kind == "fixed":
            out = self.session.buffer
            self.session.reset()
        elif self.buf:
            out = self._final(self.buf)
        self.buf = ""
        self.cands = []
        self.sel = -1
        self._shift_down = self._shift_tap = False
        return self._out(out) if out else ""

    def mode_label(self):
        if not self.bangla:
            return "EN"
        return {"avro": "অ", "popy": "প", "fixed": "ক"}[self.kind]

    def layout_name(self):
        return getattr(self, "layout_label", self.settings.get("layout", "Avro Phonetic"))

    # ---------- toggle detection ----------
    def _is_toggle(self, keyval, m):
        t = self.settings.get("toggle_key", "Ctrl+Space")
        if m.release:
            return False
        if t == "Ctrl+Space":
            return keyval == K_SPACE and m.ctrl and not m.alt and not m.shift
        if t == "Shift+Space":
            return keyval == K_SPACE and m.shift and not m.ctrl and not m.alt
        if t == "F12":
            return keyval == K_F12
        return False

    def toggle(self):
        pending = self.flush()
        self.bangla = not self.bangla
        return Action(consumed=True, commit=pending, mode_changed=True)

    def _modifier_only_toggle(self, keyval, m):
        """Right Win / Right Ctrl alone: toggles on key press, key is swallowed."""
        t = self.settings.get("toggle_key")
        want = {"Right Win": K_SUPER_R, "Right Ctrl": K_CONTROL_R}.get(t)
        if want is None or keyval != want:
            return None
        if m.release:
            return Action(consumed=True)
        return self.toggle()

    # ---------- main ----------
    def process(self, keyval, keycode, m):
        r = self._modifier_only_toggle(keyval, m)
        if r is not None:
            return r
        if keyval in (K_SHIFT_L, K_SHIFT_R):
            return self._shift_key(m)
        if not m.release:
            self._shift_tap = False      # any other key press cancels a Shift tap
        if m.release:
            return Action()
        if self._is_toggle(keyval, m):
            return self.toggle()
        if keyval in MODIFIER_KEYSYMS:
            return Action()
        if not self.bangla:
            return Action()
        if m.ctrl or m.alt or m.super:
            return self._pass(self.flush())
        if self.kind == "fixed":
            return self._fixed(keyval, keycode, m)
        return self._phonetic(keyval, m)

    def _shift_key(self, m):
        """Popy: a Shift key pressed and released on its own (a tap) is the "do not merge" key:
        before a consonant it joins, before a vowel it gives the independent vowel.  The key is never
        consumed; holding it or tapping it again changes nothing more (it is added once)."""
        if not m.release:
            if not self._shift_down and not (m.ctrl or m.alt or m.super):
                self._shift_tap = True
            self._shift_down = True
            return Action()
        tap = self._shift_tap and not (m.ctrl or m.alt or m.super)
        self._shift_down = self._shift_tap = False
        if tap and self.bangla and self.kind == "popy" and self.buf and not self.buf.endswith(popy.SH):
            self.buf += popy.SH
            self._refresh_cands()
            a = self._state_action(False)
            a.update = True
            return a
        return Action()

    def _pass(self, commit=""):
        return Action(False, commit)

    def _state_action(self, consumed=True, commit=""):
        a = Action(consumed, commit)
        txt = self.current_text()
        a.preedit = self._out(txt) if txt else ""
        a.candidates = [self._out(c) for c in self.cands]
        a.cursor = self.sel
        if self.kind in ("avro", "popy") and self.buf and self.settings.get("show_preview", True):
            a.aux = self.buf.replace(popy.SH, "\u21e7")
        return a

    # ----- phonetic (Avro / Popy)
    def _refresh_cands(self):
        """Preview window: the direct conversion first, then dictionary suggestions.
        Popy: suggestions only while auto-correct is on (they come from the Popy word list)."""
        self.cands, self.sel = [], -1
        if not self.buf or not self.settings.get("show_preview", True):
            return
        if self.kind == "popy":
            if not self._popy_auto():
                return   # preview shows only the typed English letters
            conv = popy.convert(self.buf)
            try:
                sug = popy_dict.get().suggestions(conv, 8)
            except Exception:
                sug = []
            if sug:
                self.cands = [conv] + [w for w in sug if w != conv]
        elif self.kind == "avro":
            conv = self._avro.convert(self.buf)
            self.cands = [conv]
            if self.settings.get("avro_suggestions", True):
                try:
                    for w in avro_phonetic.suggestions(self.buf, 8):
                        if w not in self.cands:
                            self.cands.append(w)
                except Exception:
                    pass

    def _phonetic(self, keyval, m):
        if keyval == K_BACKSPACE:
            if self.buf:
                self.buf = self.buf[:-1]
                self._refresh_cands()
                return self._state_action()
            return Action()
        if keyval == K_ESCAPE:
            if self.buf:
                self.buf = ""; self.cands = []; self.sel = -1
                return self._state_action()
            return Action()
        if keyval in (K_DOWN, K_UP) and self.cands:
            n = len(self.cands)
            self.sel = (0 if self.sel < 0 else (self.sel + (1 if keyval == K_DOWN else -1)) % n) \
                if self.sel >= 0 or keyval == K_DOWN else n - 1
            return self._state_action()
        if keyval in (K_SPACE, K_RETURN, K_KP_ENTER, K_TAB):
            if not self.has_text():
                return Action()
            text = self.cands[self.sel] if self.sel >= 0 and self.cands else None
            commit = self._out(text) if text is not None else self.flush()
            self.buf = ""; self.cands = []; self.sel = -1
            if keyval == K_SPACE:
                return Action(True, commit + " ")
            return Action(False, commit)
        if keyval in (K_LEFT, K_RIGHT, K_HOME, K_END, K_DELETE, K_PGUP, K_PGDN, K_UP, K_DOWN):
            return self._pass(self.flush())
        if 0x21 <= keyval <= 0x7E:
            if self.sel >= 0 and self.cands:  # typing after navigating: accept candidate first
                pre = self._out(self.cands[self.sel])
                self.buf = ""; self.cands = []; self.sel = -1
                self.buf += chr(keyval)
                a = self._state_action(True, pre)
                return a
            self.buf += chr(keyval)
            self._refresh_cands()
            return self._state_action()
        return self._pass(self.flush())

    def select_candidate(self, index):
        """Mouse click on a candidate: commit it and clear the word."""
        if 0 <= index < len(self.cands):
            text = self._out(self.cands[index])
            self.buf = ""; self.cands = []; self.sel = -1
            return Action(True, text)
        return Action()

    # ----- fixed layouts
    def _fixed(self, keyval, keycode, m):
        s = self.session
        if keyval == K_BACKSPACE:
            if s.backspace():
                return self._state_action()
            return Action()
        if keyval == K_ESCAPE:
            if s.buffer:
                s.reset()
                return self._state_action()
            return Action()
        if keyval in (K_SPACE, K_RETURN, K_KP_ENTER, K_TAB):
            commit = self.flush()
            if keyval == K_SPACE:
                return Action(True, commit + " ")
            return Action(False, commit)
        if keyval in (K_LEFT, K_RIGHT, K_HOME, K_END, K_DELETE, K_UP, K_DOWN, K_PGUP, K_PGDN):
            return self._pass(self.flush())
        r = s.key(keycode, m.shift, m.caps, m.altgr)
        if r.handled:
            return self._state_action()
        return self._pass(self._out(r.commit) if r.commit else self.flush())
