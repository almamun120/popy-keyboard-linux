"""Popy dictionary: auto-correct and suggestions from the bundled word list (popy_words.txt.gz).

The list is built from the Bangla dictionary database (word <TAB> frequency).  A typed word is
compared with the list through a "normalisation key" that folds the letters Bangla typists
confuse (ই/ঈ, ি/ী, উ/ঊ, ু/ূ, শ/ষ/স, ণ/ন, ৎ/ত, ZWJ/ZWNJ ...).
"""
import bisect
import gzip
import os
import unicodedata

from . import config

_FOLD = str.maketrans({
    "ঈ": "ই", "ী": "ি", "ঊ": "উ", "ূ": "ু", "শ": "স", "ষ": "স", "ণ": "ন", "ৎ": "ত",
    "‌": None, "‍": None,
})
_NUKTA = {"ড": "ড়", "ঢ": "ঢ়", "য": "য়"}


def _compose(s):
    """Precomposed ড় ঢ় য় (U+09DC U+09DD U+09DF) for the decomposed base + nukta forms."""
    s = s.replace("ড়", "ড়").replace("ঢ়", "ঢ়").replace("য়", "য়")
    return s


def normkey(word):
    return _compose(word).translate(_FOLD)


def is_bangla_word(text):
    """Only plain Bangla words are looked up (no digits, Latin letters, punctuation)."""
    if len(text) < 2:
        return False
    for ch in text:
        o = ord(ch)
        if not (0x0980 <= o <= 0x09FF or o in (0x200C, 0x200D)):
            return False
        if 0x09E6 <= o <= 0x09EF or o in (0x09F3, 0x09F7, 0x09E4, 0x09E5):   # digits, punctuation
            return False
    return True


class PopyDictionary:
    def __init__(self, path=None):
        self.freq = {}          # word -> frequency
        self.keys = []          # sorted unique normalisation keys
        self.by_key = {}        # key -> [words sorted by frequency desc]
        self.loaded = False
        self.path = path

    # ---------- loading ----------
    @staticmethod
    def find_file():
        names = ("popy_words.txt.gz", "popy_words.txt")
        bases = [os.path.join(config.user_data_dir()), "/usr/share/%s" % config.APP,
                 config.package_data_dir()]
        for b in bases:
            for n in names:
                p = os.path.join(b, n)
                if os.path.isfile(p):
                    return p
        return None

    def load(self):
        if self.loaded:
            return
        self.loaded = True
        path = self.path or self.find_file()
        if not path:
            return
        opener = gzip.open if path.endswith(".gz") else open
        by_key = {}
        with opener(path, "rt", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                w = _compose(parts[0])      # one spelling for য় ড় ঢ়
                if not w:
                    continue
                try:
                    fr = int(parts[1]) if len(parts) > 1 else 1
                except ValueError:
                    fr = 1
                if w in self.freq:
                    self.freq[w] += fr
                    continue
                self.freq[w] = fr
                by_key.setdefault(normkey(w), []).append(w)
        for k, ws in by_key.items():
            ws.sort(key=lambda x: -self.freq[x])
        self.by_key = by_key
        self.keys = sorted(by_key)

    # ---------- queries ----------
    def contains(self, word):
        self.load()
        return word in self.freq

    def correct(self, word):
        """Auto-correct: the word itself if it is in the list, else the most frequent word with
        the same normalisation key, else the word unchanged."""
        if not is_bangla_word(word):
            return word
        self.load()
        if word in self.freq:
            return word
        ws = self.by_key.get(normkey(word))
        return ws[0] if ws else word

    def suggestions(self, word, limit=8):
        """Same-key words first (best first), then words that start with the typed letters."""
        if not is_bangla_word(word):
            return []
        self.load()
        k = normkey(word)
        out = list(self.by_key.get(k, ()))[:limit]
        if len(out) < limit and self.keys:
            lo = bisect.bisect_left(self.keys, k)
            hi = lo
            n = len(self.keys)
            scan = 0
            cand = []
            while hi < n and self.keys[hi].startswith(k) and scan < 20000:
                if self.keys[hi] != k:
                    cand.append(self.by_key[self.keys[hi]][0])
                hi += 1
                scan += 1
            cand.sort(key=lambda w: -self.freq[w])
            for w in cand:
                if w not in out:
                    out.append(w)
                    if len(out) >= limit:
                        break
        return out[:limit]


_DICT = None


def get():
    global _DICT
    if _DICT is None:
        _DICT = PopyDictionary()
    return _DICT
