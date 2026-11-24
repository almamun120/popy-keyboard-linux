import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from avrokb.bijoy import unicode_to_bijoy as u

CASES = {
    'আমি': 'Avwg', 'বাংলা': 'evsjv', 'কর্ম': 'Kg©', 'ক্ষ': '¶', 'বিদ্যালয়': 'we`¨vjq',
    'শ্রী': 'kªx', 'আমার সোনার বাংলা': 'Avgvi †mvbvi evsjv', 'কেন': '†Kb', 'ভূমি': 'f‚wg',
    'দুঃখ': '`ytL', 'ক্রিয়া': 'wµqv', '': '',
}


class T(unittest.TestCase):
    def test_cases(self):
        for k, v in CASES.items():
            self.assertEqual(u(k), v, k)


if __name__ == '__main__':
    unittest.main()
