import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from avrokb.avro_phonetic import convert, suggestions

CASES = {
    'ami': 'আমি', 'amar': 'আমার', 'bangla': 'বাংলা', 'tumi': 'তুমি', 'hoy': 'হ\u09df', 'amader': 'আমাদের',
    'aj': 'আজ', 'bhalo': 'ভাল', 'valo': 'ভাল', 'bondhu': 'বন্ধু', 'prem': 'প্রেম', 'krom': 'ক্রম',
    'khaoya': 'খাও\u09df\u09be', 'kothaY': 'কথা\u09df', 'kkh': 'ক্ষ', 'rri': 'ঋ', 'T': 'ট', 'Th': 'ঠ', 'D': 'ড', 'Dh': 'ঢ',
    'N': 'ণ', 'SH': 'ষ', 'ng': 'ং', 'ami.': 'আমি।', '1234': '১২৩৪', '(ami)': '(আমি)', 'bangladesh': 'বাংলাদেশ',
    'ekhane': 'এখানে', 'sundor': 'সুন্দর', ':': 'ঃ', 'ghor': 'ঘর', ',,': '্‌',
}


class T(unittest.TestCase):
    def test_cases(self):
        for k, v in CASES.items():
            self.assertEqual(convert(k), v, k)

    def test_suggest(self):
        s = suggestions('bangla')
        self.assertEqual(s[0], 'বাংলা')
        self.assertIn('বাংলাদেশ', suggestions('bangla', limit=40))


if __name__ == '__main__':
    unittest.main()
