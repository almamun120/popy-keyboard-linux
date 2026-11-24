import os, sys, unittest
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
from avrokb import core, config
from avrokb.layouts import EVDEV

INV = {v: k for k, v in EVDEV.items()}
LDIR = os.path.join(HERE, "..", "avrokb", "data", "layouts")


def mk(**kw):
    s = dict(config.DEFAULTS); s.update(kw)
    return core.TypingCore(s, [LDIR])


def type_str(c, text):
    out = ""
    last = None
    for ch in text:
        kv = ord(ch)
        a = c.process(kv, 0, core.Mods(shift=ch.isupper()))
        out += a.commit
        last = a
        if not a.consumed:
            out += ch
    return out, last


class T(unittest.TestCase):
    def test_avro(self):
        c = mk(layout="Avro Phonetic")
        out, last = type_str(c, "ami ")
        self.assertEqual(out, "আমি ")

    def test_popy(self):
        c = mk(layout="Popy")
        out, last = type_str(c, "amar soonar bangla ")
        self.assertEqual(out, "আমার সোনার বাংলা ")

    def test_toggle(self):
        c = mk(layout="Popy")
        a = c.process(core.K_SPACE, 57, core.Mods(ctrl=True))
        self.assertTrue(a.consumed and a.mode_changed and not c.bangla)
        out, _ = type_str(c, "ami ")
        self.assertEqual(out, "ami ")

    def test_right_win(self):
        c = mk(layout="Popy", toggle_key="Right Win")
        a = c.process(core.K_SUPER_R, 126, core.Mods())
        self.assertTrue(a.consumed and not c.bangla)
        a = c.process(core.K_SUPER_R, 126, core.Mods(release=True))
        self.assertTrue(a.consumed)
        self.assertFalse(c.bangla)

    def test_ansi(self):
        c = mk(layout="Popy", output_ansi=True)
        out, _ = type_str(c, "ami ")
        self.assertEqual(out, "Avwg ")

    def test_fixed(self):
        c = mk(layout="UniBijoy")
        c.process(ord("m"), INV["M"], core.Mods())
        a = c.process(ord("d"), INV["D"], core.Mods())
        self.assertEqual(a.preedit, "মি")
        a = c.process(core.K_SPACE, 57, core.Mods())
        self.assertEqual(a.commit, "মি ")

    def test_backspace_and_pass(self):
        c = mk(layout="Popy")
        c.process(ord("k"), 0, core.Mods())
        a = c.process(core.K_BACKSPACE, 0, core.Mods())
        self.assertTrue(a.consumed and a.preedit == "")
        a = c.process(core.K_BACKSPACE, 0, core.Mods())
        self.assertFalse(a.consumed)

    def test_preview_popy_and_toggle(self):
        c = mk(layout="Popy")
        a = c.process(ord("k"), 0, core.Mods())
        a = c.process(ord("h"), 0, core.Mods())
        self.assertEqual(a.candidates, [])
        self.assertEqual(a.aux, "kh")
        c2 = mk(layout="Popy", show_preview=False)
        a = c2.process(ord("k"), 0, core.Mods())
        self.assertEqual(a.candidates, [])
        self.assertEqual(a.preedit, "\u0995")

    def test_avro_preview_and_click(self):
        c = mk(layout="Avro Phonetic", avro_suggestions=True)
        for ch in "bangla":
            a = c.process(ord(ch), 0, core.Mods())
        self.assertEqual(a.aux, "bangla")
        self.assertEqual(a.candidates[0], "\u09ac\u09be\u0982\u09b2\u09be")
        self.assertTrue(len(a.candidates) > 1)
        r = c.select_candidate(1)
        self.assertEqual(r.commit, a.candidates[1])
        self.assertEqual(c.buf, "")

    def test_engine_names(self):
        d = dict(config.DEFAULTS)
        names = ["UniBijoy", "National (Jatiya)"]
        self.assertEqual(config.engine_layout("popy-layout", d, names), "Popy")
        self.assertEqual(config.engine_layout("popy-fixed-national-jatiya", d, names), "National (Jatiya)")
        c = core.TypingCore(d, [LDIR], engine_name="popy-fixed-unibijoy")
        self.assertEqual(c.kind, "fixed")
        c = core.TypingCore(d, [LDIR], engine_name="popy-layout")
        self.assertEqual(c.kind, "popy")


if __name__ == "__main__":
    unittest.main()
