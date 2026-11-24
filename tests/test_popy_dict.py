import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from avrokb import core, popy_dict, popy


def mk(**kw):
    s = {"layout": "Popy", "show_preview": True, "popy_autocorrect": True}
    s.update(kw)
    return core.TypingCore(settings=s)


def shift_tap(c, key=core.K_SHIFT_L):
    c.process(key, 0, core.Mods())
    return c.process(key, 0, core.Mods(release=True))


def typ(c, text):
    a = None
    for ch in text:
        a = c.process(ord(ch), 0, core.Mods())
    return a


class T(unittest.TestCase):
    def test_normkey_folds(self):
        k = popy_dict.normkey
        self.assertEqual(k("সীমা"), k("সিমা"))
        self.assertEqual(k("শহর"), k("সহর"))
        self.assertEqual(k("কথায়"), k("কথায়"))

    def test_correct_keeps_known_word(self):
        d = popy_dict.get()
        self.assertEqual(d.correct("বাংলা"), "বাংলা")

    def test_correct_folds_to_frequent_word(self):
        d = popy_dict.get()
        # ষ typed where the dictionary word uses স (same key) -> the dictionary spelling
        w = d.correct("তুমী")
        self.assertEqual(popy_dict.normkey(w), popy_dict.normkey("তুমি"))
        self.assertTrue(d.contains(w))

    def test_non_bangla_untouched(self):
        d = popy_dict.get()
        self.assertEqual(d.correct("abc"), "abc")
        self.assertEqual(d.correct("১২৩"), "১২৩")
        self.assertEqual(d.suggestions("x"), [])

    def test_suggestions_prefix(self):
        s = popy_dict.get().suggestions("বাংলাদে", 5)
        self.assertTrue(s and all(w.startswith("বাংলাদে") for w in s))

    def test_core_commit_autocorrect_on(self):
        c = mk()
        typ(c, "tumii")                      # তুমী -> dictionary spelling
        a = c.process(0x20, 0, core.Mods())
        self.assertTrue(a.commit.endswith(" "))
        self.assertEqual(popy_dict.normkey(a.commit.strip()), popy_dict.normkey("তুমি"))
        self.assertTrue(popy_dict.get().contains(a.commit.strip()))

    def test_core_commit_autocorrect_off(self):
        c = mk(popy_autocorrect=False)
        typ(c, "tumii")
        a = c.process(0x20, 0, core.Mods())
        self.assertEqual(a.commit, popy.convert("tumii") + " ")
        self.assertEqual(c.cands, [])

    def test_preview_suggestions(self):
        c = mk()
        a = typ(c, "bangla")
        self.assertEqual(a.aux, "bangla")
        self.assertEqual(a.candidates[0], "বাংলা")
        self.assertGreater(len(a.candidates), 1)

    def test_no_suggestions_when_preview_off(self):
        c = mk(show_preview=False)
        a = typ(c, "bangla")
        self.assertEqual(a.candidates, [])
        self.assertEqual(a.aux, "")

    def test_raw_candidate_bypasses_autocorrect(self):
        c = mk()
        typ(c, "tumii")
        c.process(0xFF54, 0, core.Mods())      # Down -> first candidate = what was typed
        a = c.process(0x20, 0, core.Mods())
        self.assertEqual(a.commit, popy.convert("tumii") + " ")

    def test_force_join_in_core(self):
        c = mk(popy_autocorrect=False)
        typ(c, "k")
        shift_tap(c)
        typ(c, "f")
        a = c.process(0x20, 0, core.Mods())
        self.assertEqual(a.commit, "ক্ফ ")


if __name__ == "__main__":
    unittest.main()
