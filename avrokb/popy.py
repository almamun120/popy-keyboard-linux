"""Popy layout: phonetic typing engine (Latin letters -> Bangla).

Direct port of the Android BanglaPhonetic.kt / Delphi clsPopyPhonetic.pas.
convert(buf) gives the final text; preview(buf) gives (text, has_marker) where
a trailing 'o' (after a consonant), 'q' or 's' (a tapped Shift = SH) marker is appended visibly.

Shift (the SH token, "\\x01") is the "do not merge automatically" key: before a consonant it
forces the join (t SH t = ত্ত, k SH f = ক্ফ), before a vowel it gives the independent vowel
(b o SH i = বই).  q only makes special letters and signs.
"""
SH = "\x01"
HASANTA = "্"; ZWNJ = "‌"; ZWJ = "‍"; NUKTA = "়"

CONSONANTS = {
    "k": "ক", "kh": "খ", "g": "গ", "gh": "ঘ", "nng": "ঙ",
    "c": "চ", "ch": "ছ", "j": "জ", "jh": "ঝ", "nnn": "ঞ",
    "tt": "ট", "tth": "ঠ", "dd": "ড", "ddh": "ঢ", "nn": "ণ",
    "t": "ত", "th": "থ", "d": "দ", "dh": "ধ", "n": "ন",
    "p": "প", "f": "ফ", "ph": "ফ", "b": "ব", "bh": "ভ", "v": "ভ",
    "m": "ম", "y": "য়", "z": "য", "r": "র", "l": "ল",
    "s": "স", "ss": "শ", "sss": "ষ", "h": "হ",
    "x": "ক" + HASANTA + "ষ",
    "rr": "ড়", "rrh": "ঢ়",
}
VOWELS = {
    "o": ("অ", ""), "a": ("আ", "া"), "i": ("ই", "ি"), "ii": ("ঈ", "ী"),
    "u": ("উ", "ু"), "uu": ("ঊ", "ূ"), "rrr": ("ঋ", "ৃ"), "e": ("এ", "ে"),
    "oi": ("ঐ", "ৈ"), "oo": ("ও", "ো"), "ou": ("ঔ", "ৌ"),
}
DIGITS = "০১২৩৪৫৬৭৮৯"

PAIRS = frozenset("""
কক কট কত কদ কন কম কয কর কল কষ
কস খয খর গগ গধ গন গম গয গর গল
ঘন ঘয ঘর ঙক ঙখ ঙগ ঙঘ ঙম ঙয ঙর
চচ চছ চঞ চয ছয ছর জজ জঝ জঞ জয
জর ঝয ঞচ ঞছ ঞজ ঞঝ টট টম টয টর
ঠয ডড ডম ডয ডর ঢয ঢর ণট ণঠ ণড
ণঢ ণম ণয তন তম তয তর থয থর দগ
দঘ দভ দম দয দর ধন ধম ধয ধর নট
নঠ নড নত নথ নদ নধ নম নয নস পট
পত পথ পন পপ পয পর পল পস ফট ফয
ফর ফল বজ বদ বধ বয বর বল ভয ভর
ভল মন মপ মফ মভ মম ময মর মল যয
লক লগ লট লড লপ লফ লম লয লল শচ
শছ শত শন শম শয শর শল ষক ষট ষঠ
ষণ ষপ ষফ ষম ষয সক সখ সট সত সথ
সন সপ সফ সম সয সর সল হণ হন হম
হয হর হল
""".split())


# Greedy mode (default on): the 163 listed pairs join by themselves.  Off: NOTHING joins by itself - every
# conjunct (also reph, ra-phala, ya-phala, qn) needs a Shift tap; r and z are independent letters;
# o has no role after a consonant.
GREEDY = True


def joinable(a, b):
    """Does consonant a + hasanta + consonant b form a real Bangla conjunct? (RA = reph joins all)"""
    return a == "\u09b0" or (a + b) in PAIRS


def _is_letter(c):
    return "a" <= c <= "z"


def _ends_plain_ra(out):
    return bool(out) and out[-1] == "র" and (len(out) < 2 or out[-2] != HASANTA)


def _run(inp):
    src = "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in inp)
    out = []  # list of str pieces joined lazily; keep as str for simplicity
    out = ""
    cons_after = False
    word_start = True
    ra_initial = False
    q_break = False
    last = ""
    last_letter = ""
    phala = False       # the last consonant is a ra-phala / ya-phala: no automatic join after it
    shift = False       # Shift (SH) was tapped: the next consonant joins / the next vowel is independent
    pending = " "
    # Non-greedy mode: Shift is a POSTFIX - it joins the consonant just typed to the one before it
    # (km, Shift = ক্ম).  lstart = index in out where that last consonant begins (-1 = not applicable).
    lstart = -1
    lvow = None         # (index in out, independent form) of a vowel sign just typed after a consonant
    lra = False         # that consonant was a ya-phala after a word-initial ra (র‍্য)
    ltok = ""
    i = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c == SH and not GREEDY:  # non-greedy: Shift joins the last consonant to the previous one
            if lvow is not None:    # ... or turns the vowel sign just typed into an independent vowel (ka, Shift = কআ)
                out = out[:lvow[0]] + lvow[1]
                lvow = None
            if lstart > 0:
                prev = out[lstart - 1]
                if ("ক" <= prev <= "হ") or prev in "ড়ঢ়য়" or prev == "ৎ" or (ltok == "z" and "অ" <= prev <= "ঔ"):
                    out = out[:lstart] + (ZWJ + HASANTA if lra else HASANTA) + out[lstart:]
            lstart = -1
            i += 1
            pending = " "
            continue
        if c == SH:                 # a tapped Shift: shows as "s" until the next key uses it
            shift = True
            i += 1
            pending = "s" if i == n else " "
            continue
        lstart = -1
        lvow = None
        was_ra = ra_initial; ra_initial = False
        was_q = q_break; q_break = False
        was_shift = shift; shift = False
        pending = " "
        if c == "," and src.startswith(",,", i):
            out += HASANTA + ZWNJ; cons_after = False; word_start = False; i += 2; continue
        if c == "q":
            nx = src[i + 1] if i + 1 < n else ""
            if nx == "w":
                out += "ঃ"; cons_after = False; word_start = False; i += 2; continue
            if nx in (".", ","):
                out += "?" if nx == "." else "!"
                cons_after = False; word_start = True; i += 2; continue
            if nx == "q":
                out += "ঁ"; cons_after = False; word_start = False; i += 2; continue
            if nx == "h":
                lstart = len(out); ltok = "h"
                out += "হ"; cons_after = True; word_start = False; last = "h"; last_letter = "হ"; i += 2; continue
            if nx == "z" and not (cons_after and _ends_plain_ra(out)):
                lstart = len(out); ltok = "z"
                out += "য"; cons_after = True; word_start = False; last = "z"; last_letter = "য"; i += 2; continue
            if nx == "s" and not (cons_after and last == "s"):
                if cons_after and was_shift:
                    out += HASANTA
                lstart = len(out); ltok = "sss"
                out += "ষ"; cons_after = True; word_start = False; last = "sss"; last_letter = "ষ"; i += 2; continue
            if nx == "x":
                out += "ক" + HASANTA + "স"; cons_after = True; word_start = False; last = "x"; last_letter = "স"; i += 2; continue
            if nx == "n" and not (cons_after and last in ("n", "nn")):
                # ঞ follows the list too (it joins by itself only where the pair is listed); Shift forces it
                if cons_after and (was_shift or (GREEDY and joinable(last_letter, "ঞ"))):
                    out += HASANTA
                lstart = len(out); ltok = "nnn"
                out += "ঞ"; cons_after = True; word_start = False; last = "nnn"; last_letter = "ঞ"; i += 2; continue
            if nx == "r" and not (cons_after and last == "r"):
                # qr = RI (vowel at word start / after a vowel), RI-KAR after a consonant;
                # after RA the q is only a separator (r SH r = RA + hasanta + RA)
                out += "ৃ" if cons_after else "ঋ"
                cons_after = False; word_start = False; i += 2; continue
            if cons_after:
                if nx == "z" and _ends_plain_ra(out):
                    out += ZWJ + HASANTA + "য"
                    cons_after = True; word_start = False; last = "z"; last_letter = "য"; i += 2; continue
                after = src[i + 2] if i + 2 < n else " "
                if src.startswith("qt", i) and after not in ("h", "t") and last not in ("t", "tt"):
                    out += "ৎ"; cons_after = False; word_start = False; i += 2; continue
                i += 1
                q_break = True          # any other q: nothing, it only splits the token (tqt = তত)
                if i == n:
                    pending = "q"
                continue
            if src.startswith("qt", i):
                out += "ৎ"; word_start = False; i += 2; continue
            if src.startswith("qk", i):
                out += "৳"; word_start = False; i += 2; continue
            if i + 1 < n and _is_letter(src[i + 1]):
                q_break = True; i += 1; continue     # q + any other letter: the q just goes away
            out += "q"; cons_after = False; word_start = False; i += 1
            if i == n:
                pending = "Q"
            continue

        matched = False
        ln = min(3, n - i)
        while ln >= 1:
            tok = src[i:i + ln]
            if tok == "w":
                if cons_after:
                    out += HASANTA + "ব"; cons_after = True; last = "w"; last_letter = "ব"
                else:
                    out += "ও"; cons_after = False
                word_start = False; i += 1; matched = True; break
            if tok == "ng":
                out += "ং"; cons_after = False; word_start = False; i += 2; matched = True; break
            cons = CONSONANTS.get(tok)
            if cons is not None:
                starts_word = word_start and not cons_after
                was_phala = phala
                phala = False
                if tok == "z" and not cons_after and not was_q and out and "অ" <= out[-1] <= "ঔ" and (GREEDY or was_shift):
                    out += HASANTA + cons
                    phala = True
                elif tok == "z" and cons_after and was_ra and (GREEDY or was_shift):
                    out += ZWJ + HASANTA + cons
                    phala = True
                else:
                    # Greedy part: hasanta only for the listed conjunct pairs (PAIRS); b and y never join by
                    # themselves; nothing joins after a ra-phala / ya-phala (a ya-phala may follow a
                    # ra-phala: ব্র্যান, and য়: য়্য).  A tapped Shift (SH) forces the join; য় is never a phala.
                    joined = False
                    if cons_after and tok != "y" and (was_shift or (GREEDY and tok != "b" and (
                            (tok == "z" and last == "y")
                            or ((not was_phala or (tok == "z" and last_letter == "র")) and joinable(last_letter, cons[0]))))):
                        out += HASANTA
                        joined = True
                    if not joined:
                        lstart = len(out); ltok = tok; lra = (tok == "z" and was_ra)
                    out += cons
                    phala = joined and cons[0] in ("র", "য")
                last_letter = cons[-1]
                ra_initial = tok == "r" and starts_word
                last = tok
                cons_after = True; word_start = False
                i += ln; matched = True; break
            v = VOWELS.get(tok)
            if v is not None:
                if cons_after and not was_shift:
                    lvow = (len(out), v[0])
                out += v[1] if (cons_after and not was_shift) else v[0]
                if tok == "o" and cons_after and i + ln == n:
                    pending = "o"
                cons_after = False; word_start = False
                i += ln; matched = True; break
            ln -= 1
        if matched:
            continue
        if "0" <= c <= "9":
            out += DIGITS[ord(c) - 48]
        elif c == ".":
            out += "।"
        else:
            out += inp[i]
        cons_after = False; word_start = True; i += 1
    return out, pending


def convert(buf):
    return _run(buf)[0]


def preview(buf):
    text, p = _run(buf)
    if p in ("o", "q", "s"):
        return text + p, True
    return text, False
