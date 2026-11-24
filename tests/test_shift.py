import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from avrokb import core, popy

M = core.Mods


def mk(**kw):
    s = {"layout": "Popy", "show_preview": True, "popy_autocorrect": False}
    s.update(kw)
    return core.TypingCore(settings=s)


def key(c, ch, **m):
    return c.process(ord(ch), 0, M(**m))


def tap(c, k=core.K_SHIFT_L):
    c.process(k, 0, M())
    return c.process(k, 0, M(shift=True, release=True))


def word(c):
    return c.process(0x20, 0, M()).commit


class T(unittest.TestCase):
    def test_join_geminate(self):
        c = mk(); key(c, "t"); tap(c); key(c, "t")
        self.assertEqual(word(c), "ত্ত ")

    def test_join_non_listed_pair(self):
        c = mk(); key(c, "k"); tap(c); key(c, "f")
        self.assertEqual(word(c), "ক্ফ ")

    def test_independent_vowel(self):
        c = mk()
        for ch in "bo":
            key(c, ch)
        tap(c); key(c, "i")
        self.assertEqual(word(c), "বই ")

    def test_marker_s_then_gone(self):
        c = mk(); key(c, "t")
        a = tap(c)
        self.assertTrue(a.update and not a.consumed)
        self.assertEqual(a.preedit, "তs")           # shown like the q / o marker
        self.assertEqual(a.aux, "t⇧")
        a = key(c, "t")
        self.assertEqual(a.preedit, "ত্ত")          # the marker is used up

    def test_tap_is_added_once(self):
        c = mk(); key(c, "k")
        tap(c); tap(c); tap(c)
        key(c, "f")
        self.assertEqual(word(c), "ক্ফ ")
        self.assertEqual(c.buf, "")

    def test_hold_with_key_repeat_is_one_tap(self):
        c = mk(); key(c, "k")
        for _ in range(5):                            # auto-repeat: many presses, one release
            c.process(core.K_SHIFT_L, 0, M(shift=True))
        c.process(core.K_SHIFT_L, 0, M(shift=True, release=True))
        self.assertEqual(c.buf, "k" + popy.SH)

    def test_backspace_removes_it(self):
        c = mk(); key(c, "k"); tap(c)
        a = c.process(core.K_BACKSPACE, 0, M())
        self.assertEqual(a.preedit, "ক")
        key(c, "f")
        self.assertEqual(word(c), "কফ ")

    def test_shift_with_letter_is_not_a_tap(self):
        c = mk()
        c.process(core.K_SHIFT_L, 0, M())
        key(c, "T", shift=True)
        c.process(core.K_SHIFT_L, 0, M(shift=True, release=True))
        self.assertEqual(c.buf, "T")

    def test_ctrl_shift_is_not_a_tap(self):
        c = mk(); key(c, "k")
        c.process(core.K_CONTROL_L, 0, M())
        c.process(core.K_SHIFT_L, 0, M(ctrl=True))
        c.process(core.K_SHIFT_L, 0, M(ctrl=True, shift=True, release=True))
        self.assertEqual(c.buf, "k")

    def test_empty_buffer_ignored(self):
        c = mk(); a = tap(c)
        self.assertFalse(a.update); self.assertEqual(c.buf, "")

    def test_right_shift_and_not_consumed(self):
        c = mk(); key(c, "n")
        a = tap(c, core.K_SHIFT_R)
        self.assertFalse(a.consumed)
        key(c, "n")
        self.assertEqual(word(c), "ন্ন ")

    def test_other_layouts_ignore_shift_tap(self):
        c = mk(layout="Avro Phonetic"); key(c, "k"); tap(c)
        self.assertEqual(c.buf, "k")


if __name__ == "__main__":
    unittest.main()


class NonGreedyCore(unittest.TestCase):
    """popy_greedy = False: Shift is a postfix (km, Shift = ক্ম; ka, Shift = কআ)."""

    def tearDown(self):
        popy.GREEDY = True

    def test_postfix_join(self):
        c = mk(popy_greedy=False)
        for ch in "km":
            key(c, ch)
        tap(c)
        self.assertEqual(word(c), "ক্ম ")

    def test_postfix_independent_vowel(self):
        c = mk(popy_greedy=False)
        for ch in "ka":
            key(c, ch)
        tap(c)
        self.assertEqual(word(c), "কআ ")

    def test_setting_applied(self):
        mk(popy_greedy=False)
        self.assertFalse(popy.GREEDY)
        mk()
        self.assertTrue(popy.GREEDY)
