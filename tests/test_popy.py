import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from avrokb import popy

TSV = os.path.join(os.path.dirname(__file__), "typing_cases.tsv")


class T(unittest.TestCase):
    def test_cases(self):
        bad = []
        n = 0
        for line in open(TSV, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            k, v = line.split("\t")[:2]
            k = k.replace("\u21e7", popy.SH)     # ⇧ = a tapped Shift
            n += 1
            if popy.convert(k) != v:
                bad.append((k, v, popy.convert(k)))
        self.assertEqual(bad, [], "%d cases" % n)


class NonGreedy(unittest.TestCase):
    """Greedy mode off: nothing joins by itself; r, z independent; o has no role after a consonant."""

    def test_cases(self):
        popy.GREEDY = False
        try:
            bad = []
            for line in open(TSV.replace("typing_cases", "typing_cases_nongreedy"), encoding="utf-8"):
                line = line.rstrip("\n")
                if not line:
                    continue
                k, v = line.split("\t")[:2]
                k = k.replace("\u21e7", popy.SH)
                if popy.convert(k) != v:
                    bad.append((k, v, popy.convert(k)))
            self.assertEqual(bad, [])
            self.assertTrue(popy.preview("ko")[1])      # the o marker is shown as in greedy mode
        finally:
            popy.GREEDY = True


if __name__ == "__main__":
    unittest.main()
