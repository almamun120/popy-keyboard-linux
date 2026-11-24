import os, sys, unittest
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
from avrokb import layouts as L

DIR = os.path.join(HERE, "..", "avrokb", "data", "layouts")
INV = {v: k for k, v in L.EVDEV.items()}


def type_word(lay, keys, settings=None):
    s = L.LayoutSession(lay, settings)
    for k in keys:
        shift = k.isupper() and k.isalpha()
        name = k.upper() if k.isalpha() else k
        code = INV[name]
        r = s.key(code, shift=shift)
        assert r.handled, k
    return s.buffer


class T(unittest.TestCase):
    def test_load_all(self):
        lays = L.list_layouts([DIR])
        names = [l.name for l in lays]
        self.assertEqual(len(lays), 6, names)
        self.assertIn("UniBijoy", names)
        for l in lays:
            self.assertTrue(l.image_normal() is None or l.image_normal()[:2] == b"BM")

    def test_unibijoy(self):
        lay = L.load_layout(os.path.join(DIR, "UniBijoy.avrolayout"))
        self.assertEqual(type_word(lay, "md"), "\u09ae\u09bf")      # ম + ি
        self.assertEqual(type_word(lay, "1d"), "\u09e7\u0987")      # digit then kar -> independent vowel
        self.assertEqual(type_word(lay, "mgg"), "\u09ae\u09cd\u200c")  # hasanta twice -> ZWNJ

    def test_reph(self):
        lay = L.load_layout(os.path.join(DIR, "UniBijoy.avrolayout"))
        s = L.LayoutSession(lay)
        s.buffer = "\u0995\u09ae"
        s.key(INV["A"], shift=True)  # shift+A = র্
        self.assertEqual(s.buffer, "\u0995\u09b0\u09cd\u09ae")  # কর্ম
        s2 = L.LayoutSession(lay, L.Settings(old_style_reph=False))
        s2.buffer = "\u0995\u09ae"
        s2.key(INV["A"], shift=True)
        self.assertEqual(s2.buffer, "\u0995\u09ae\u09b0\u09cd")


if __name__ == "__main__":
    unittest.main()
