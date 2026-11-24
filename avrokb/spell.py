"""Bangla spell checking on top of the Avro word list (Database.db3).  GUI independent."""
import os
import re
import sqlite3

from . import avro_phonetic

WORD_RE = re.compile(r"[ঀ-৿‌‍]+")
_DIGITS = re.compile(r"^[০-৯]+$")


class SpellChecker:
    def __init__(self, db_path=None, custom_path=None):
        self.dict = avro_phonetic.Dictionary(db_path)
        self.custom_path = custom_path
        self.custom = set()
        self.ignored = set()
        self._by_first = None
        self._suffixes = None
        self._load_custom()

    # --- data
    def _ensure(self):
        self.dict._load()
        if self._by_first is None:
            self._words = set(self.dict._words)
            by = {}
            for w in self.dict._words:
                by.setdefault(w[0], []).append(w)
            self._by_first = by
            sfx = set()
            try:
                con = sqlite3.connect(self.dict.path)
                sfx = {b for (b,) in con.execute("select Bangla from Suffix") if b}
                con.close()
            except Exception:
                pass
            self._suffixes = sorted(sfx, key=len, reverse=True)

    def _load_custom(self):
        if self.custom_path and os.path.exists(self.custom_path):
            with open(self.custom_path, encoding="utf-8") as f:
                self.custom = {l.strip() for l in f if l.strip()}

    def add_custom(self, word):
        self.custom.add(word)
        if self.custom_path:
            os.makedirs(os.path.dirname(self.custom_path), exist_ok=True)
            with open(self.custom_path, "w", encoding="utf-8") as f:
                f.write("\n".join(sorted(self.custom)) + "\n")

    def ignore(self, word):
        self.ignored.add(word)

    # --- checking
    def is_known(self, word):
        self._ensure()
        if word in self._words or word in self.custom or word in self.ignored or _DIGITS.match(word):
            return True
        for s in self._suffixes:
            if word.endswith(s) and len(word) > len(s) and word[:-len(s)] in self._words:
                return True
        return False

    def find_errors(self, text):
        """[(start, end, word)] for every unknown Bangla word."""
        res = []
        for m in WORD_RE.finditer(text):
            w = m.group().strip("‌‍")
            if w and not self.is_known(w):
                res.append((m.start(), m.end(), m.group()))
        return res

    @staticmethod
    def _distance(a, b, cap=3):
        if abs(len(a) - len(b)) > cap:
            return cap + 1
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i]
            best = i
            for j, cb in enumerate(b, 1):
                v = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
                cur.append(v)
                best = min(best, v)
            if best > cap:
                return cap + 1
            prev = cur
        return prev[-1]

    def suggest(self, word, limit=8):
        self._ensure()
        cands = []
        for first in {word[0]} | self._neighbors(word[0]):
            for w in self._by_first.get(first, ()):
                if abs(len(w) - len(word)) <= 2:
                    d = self._distance(word, w, 2)
                    if d <= 2:
                        cands.append((d, abs(len(w) - len(word)), w))
        cands.sort()
        return [w for _, _, w in cands[:limit]]

    @staticmethod
    def _neighbors(ch):
        groups = ["ইঈ", "উঊ", "সশষ", "নণ", "তট", "দড", "থঠ", "ধঢ", "জয", "বভ", "কখ", "গঘ", "চছ", "পফ"]
        for g in groups:
            if ch in g:
                return set(g) - {ch}
        return set()
