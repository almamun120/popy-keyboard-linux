import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from avrokb.spell import SpellChecker


class T(unittest.TestCase):
    def test_spell(self):
        sc = SpellChecker(custom_path=os.path.join(tempfile.mkdtemp(), "c.txt"))
        self.assertEqual(sc.find_errors("বাংলা ভাষা"), [])
        errs = sc.find_errors("আমি বাংলাা ভালোবাসি")
        words = [w for _, _, w in errs]
        self.assertIn("বাংলাা", words)
        s = sc.suggest("বাংলাা")
        self.assertIn("বাংলা", s)
        sc.add_custom("বাংলাা")
        self.assertEqual([w for _, _, w in sc.find_errors("বাংলাা")], [])


if __name__ == "__main__":
    unittest.main()
