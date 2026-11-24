"""Classic Avro Phonetic (English letters -> Bangla). Port of Delphi clsEnglishToBangla.pas.

Suggestions: simplified - dictionary words (Database.db3) that start with the converted
word, shortest first (the Delphi popup uses a regex based phonetic search).
"""
import bisect
import os
import sqlite3

class B:
    """Bangla characters (from BanglaChars.pas)."""
    b_0 = '০'
    b_1 = '১'
    b_2 = '২'
    b_3 = '৩'
    b_4 = '৪'
    b_5 = '৫'
    b_6 = '৬'
    b_7 = '৭'
    b_8 = '৮'
    b_9 = '৯'
    b_a = 'অ'
    b_aa = 'আ'
    b_aakar = 'া'
    b_anushar = 'ং'
    b_avagraha = 'ঽ'
    b_b = 'ব'
    b_bh = 'ভ'
    b_bisharga = 'ঃ'
    b_c = 'চ'
    b_ch = 'ছ'
    b_chandra = 'ঁ'
    b_currencydenominator16 = '৹'
    b_currencyesshar = '৺'
    b_currencynumerator1 = '৴'
    b_currencynumerator1lessthandenominator = '৸'
    b_currencynumerator2 = '৵'
    b_currencynumerator3 = '৶'
    b_currencynumerator4 = '৷'
    b_d = 'দ'
    b_dari = '।'
    b_dd = 'ড'
    b_ddh = 'ঢ'
    b_dh = 'ধ'
    b_e = 'এ'
    b_ekar = 'ে'
    b_g = 'গ'
    b_gh = 'ঘ'
    b_h = 'হ'
    b_hasanta = '্'
    b_i = 'ই'
    b_ii = 'ঈ'
    b_iikar = 'ী'
    b_ikar = 'ি'
    b_j = 'জ'
    b_jh = 'ঝ'
    b_k = 'ক'
    b_kh = 'খ'
    b_khandatta = 'ৎ'
    b_l = 'ল'
    b_lengthmark = 'ৗ'
    b_m = 'ম'
    b_n = 'ন'
    b_nga = 'ঙ'
    b_nn = 'ণ'
    b_nukta = '়'
    b_nya = 'ঞ'
    b_o = 'ও'
    b_oi = 'ঐ'
    b_oikar = 'ৈ'
    b_okar = 'ো'
    b_ou = 'ঔ'
    b_oukar = 'ৌ'
    b_p = 'প'
    b_ph = 'ফ'
    b_r = 'র'
    b_rr = 'ড়'
    b_rrh = 'ঢ়'
    b_rri = 'ঋ'
    b_rrikar = 'ৃ'
    b_rupeemark = '৲'
    b_s = 'স'
    b_sh = 'শ'
    b_ss = 'ষ'
    b_t = 'ত'
    b_taka = '৳'
    b_th = 'থ'
    b_tt = 'ট'
    b_tth = 'ঠ'
    b_u = 'উ'
    b_ukar = 'ু'
    b_uu = 'ঊ'
    b_uukar = 'ূ'
    b_vocalic_l = 'ঌ'
    b_vocalic_l_kar = 'ৢ'
    b_vocalic_ll = 'ৡ'
    b_vocalic_ll_kar = 'ৣ'
    b_vocalic_rr = 'ৠ'
    b_vocalic_rr_kar = 'ৄ'
    b_y = 'য়'
    b_z = 'য'
    zwj = '\u200d'
    zwnj = '\u200c'

class AutoCorrect:
    """autodict.dct: lines 'english bangla-or-english'; lines starting with '/' are comments."""

    def __init__(self, path=None):
        self.d = {}
        path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "autodict.dct")
        try:
            with open(path, encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("/"):
                        continue
                    k, sep, v = line.partition(" ")
                    if sep:
                        self.d[k] = v.strip()
        except OSError:
            pass

    def lookup(self, word):
        return self.d.get(word)


class EnglishToBangla:
    """Port of TEnglishToBangla (classic Avro Phonetic)."""

    def __init__(self, autocorrect=True, jo_nukta=False, dictionary=None):
        self.autocorrect = autocorrect
        self.jo_nukta = "YES" if jo_nukta else "NO"
        self.dict = dictionary.d if dictionary is not None else {}
        self.text = ""
        self.pos = 1
        self.rs = ""
        self.ln = 0

    # ---- primitives ----
    @staticmethod
    def _mid(s, start, length):
        if start < 1:
            start = 1
        return s[start - 1:start - 1 + length]

    def cnv(self, compare, if_true):
        n = len(compare)
        if self._mid(self.text, self.pos, n) == compare:
            self.rs += if_true
            self.pos += n
            return True
        return False

    def add_rs(self, t):
        self.rs += t
        self.pos += 1

    def add_rs_ex(self, t, p=0):
        self.rs += t
        self.pos += p

    def prev_t(self):
        i = self.pos - 1
        return "" if i < 1 else self._mid(self.text, i, 1)

    def prev_tex(self, position):
        i = self.pos - position
        return "" if i < 1 else self._mid(self.text, i, 1)

    def next_t(self):
        return self._mid(self.text, self.pos + 1, 1)

    def next_tex(self, length, skipstart=0):
        return self._mid(self.text, self.pos + skipstart + 1, max(length, 1))

    def begining(self):
        t = self.prev_t()
        if not t:
            return True
        return not (t[0].isascii() and t[0].isalnum())

    @staticmethod
    def consonent(t):
        return bool(t) and t[0].lower() in "bcdfghjklmnpqrstvwxyz"

    @staticmethod
    def vowel(t):
        return bool(t) and t[0].lower() in "aeiou"

    @staticmethod
    def number(t):
        return bool(t) and t[0] in "0123456789"

    # ---- case correction / ignorable punctuation ----
    def correct_case(self, s):
        out = []
        for t in s:
            if t in "oOiIuUdDgGjnNrRsStTyYzZ" and t != "":
                out.append(t)
            elif t == "J":
                out.append("J" if self.jo_nukta == "YES" else "j")
            else:
                out.append(t.lower())
        return "".join(out)

    def cut_text(self, s):
        n = len(s)
        p = 0
        for i in range(1, n + 1):
            t = s[i - 1]
            if t in "~!@#%&*()-_=+[]{}'\";<>/?|\\.":
                p = i
            elif t == ",":
                if self._mid(s, i + 1, 1) == ",":
                    break
                p = i
            elif t == ":":
                if self._mid(s, i + 1, 1) == "`":
                    p = i
                else:
                    break
            elif t == "`":
                if i - 1 >= 1 and self._mid(s, i - 1, 1) in (".", ":"):
                    p = i
                else:
                    break
            else:
                break
        start = s[:p]
        rev = s[::-1]
        q = 0
        for i in range(1, n - p + 1):
            t = rev[i - 1]
            if t in "~!@#%&*()-_=+[]{}'\";<>/.?|\\":
                q = i
            elif t == ",":
                if self._mid(rev, i + 1, 1) == ",":
                    break
                q = i
            elif t == "`":
                if self._mid(rev, i + 1, 1) in (":", "."):
                    q = i
                else:
                    break
            elif t == ":":
                if i - 1 >= 1 and self._mid(rev, i - 1, 1) == "`":
                    q = i
                else:
                    break
            else:
                break
        end = s[len(s) - q:] if q else ""
        mid = s[p:]
        mid = mid[:len(mid) - q] if q else mid
        return start, mid, end

    # ---- main entry ----
    def convert(self, english):
        if english == "":
            return ""
        if self.autocorrect:
            item = self.dict.get(english)
            if item is not None and item == english:
                return english
        eng = self.correct_case(english)
        if self.autocorrect:
            item = self.dict.get(eng)
            if item is not None:
                self.text = item
                return self._my_convert()
            start, mid, end = self.cut_text(eng)
            item = self.dict.get(mid)
            if item is not None:
                tmp = ""
                if start:
                    self.text = start
                    tmp = self._my_convert()
                if mid:
                    self.text = item
                    tmp += self._my_convert()
                if end:
                    self.text = end
                    tmp += self._my_convert()
                return tmp
        self.text = eng
        return self._my_convert()

    def b(self):
        if self.cnv('bdh', B.b_b + B.b_hasanta + B.b_dh) is True:
            return
        if self.cnv('bhl', B.b_bh + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('bj', B.b_b + B.b_hasanta + B.b_j) is True:
            return
        if self.cnv('bd', B.b_b + B.b_hasanta + B.b_d) is True:
            return
        if self.cnv('bb', B.b_b + B.b_hasanta + B.b_b) is True:
            return
        if self.cnv('bl', B.b_b + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('bh', B.b_bh) is True:
            return
        if self.cnv('vl', B.b_bh + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('b', B.b_b) is True:
            return
        if self.cnv('v', B.b_bh) is True:
            return

    def c(self):
        if self.cnv('cNG', B.b_c + B.b_hasanta + B.b_nya) is True:
            return
        if self.cnv('cch', B.b_c + B.b_hasanta + B.b_ch) is True:
            return
        if self.cnv('cc', B.b_c + B.b_hasanta + B.b_c) is True:
            return
        if self.cnv('ch', B.b_ch) is True:
            return
        if self.cnv('c', B.b_c) is True:
            return

    def d(self):
        if self.cnv('dhn', B.b_dh + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('dhm', B.b_dh + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('dgh', B.b_d + B.b_hasanta + B.b_gh) is True:
            return
        if self.cnv('ddh', B.b_d + B.b_hasanta + B.b_dh) is True:
            return
        if self.cnv('dbh', B.b_d + B.b_hasanta + B.b_bh) is True:
            return
        if self.cnv('dv', B.b_d + B.b_hasanta + B.b_bh) is True:
            return
        if self.cnv('dm', B.b_d + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('DD', B.b_dd + B.b_hasanta + B.b_dd) is True:
            return
        if self.cnv('Dh', B.b_ddh) is True:
            return
        if self.cnv('dh', B.b_dh) is True:
            return
        if self.cnv('dg', B.b_d + B.b_hasanta + B.b_g) is True:
            return
        if self.cnv('dd', B.b_d + B.b_hasanta + B.b_d) is True:
            return
        if self.cnv('D', B.b_dd) is True:
            return
        if self.cnv('d', B.b_d) is True:
            return

    def g(self):
        if self.cnv('ghn', B.b_gh + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('Ghn', B.b_gh + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('gdh', B.b_g + B.b_hasanta + B.b_dh) is True:
            return
        if self.cnv('Gdh', B.b_g + B.b_hasanta + B.b_dh) is True:
            return
        if self.cnv('gN', B.b_g + B.b_hasanta + B.b_nn) is True:
            return
        if self.cnv('GN', B.b_g + B.b_hasanta + B.b_nn) is True:
            return
        if self.cnv('gn', B.b_g + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('Gn', B.b_g + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('gm', B.b_g + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('Gm', B.b_g + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('gl', B.b_g + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('Gl', B.b_g + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('gg', B.b_j + B.b_hasanta + B.b_nya) is True:
            return
        if self.cnv('GG', B.b_j + B.b_hasanta + B.b_nya) is True:
            return
        if self.cnv('Gg', B.b_j + B.b_hasanta + B.b_nya) is True:
            return
        if self.cnv('gG', B.b_j + B.b_hasanta + B.b_nya) is True:
            return
        if self.cnv('gh', B.b_gh) is True:
            return
        if self.cnv('Gh', B.b_gh) is True:
            return
        if self.cnv('g', B.b_g) is True:
            return
        if self.cnv('G', B.b_g) is True:
            return

    def h(self):
        if self.cnv('hN', B.b_h + B.b_hasanta + B.b_nn) is True:
            return
        if self.cnv('hn', B.b_h + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('hm', B.b_h + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('hl', B.b_h + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('h', B.b_h) is True:
            return

    def j_up(self):
        if self.cnv('jjh', B.b_j + B.b_hasanta + B.b_jh) is True:
            return
        if self.cnv('jNG', B.b_j + B.b_hasanta + B.b_nya) is True:
            return
        if self.cnv('jh', B.b_jh) is True:
            return
        if self.cnv('jj', B.b_j + B.b_hasanta + B.b_j) is True:
            return
        if self.cnv('j', B.b_j) is True:
            return
        if self.jo_nukta == 'YES':
            if self.cnv('J', B.b_j + B.b_nukta) is True:
                return
        else:
            if self.cnv('J', B.b_j) is True:
                return

    def k(self):
        if self.cnv('kkhN', B.b_k + B.b_hasanta + B.b_ss + B.b_hasanta + B.b_nn) is True:
            return
        if self.cnv('kShN', B.b_k + B.b_hasanta + B.b_ss + B.b_hasanta + B.b_nn) is True:
            return
        if self.cnv('kkhm', B.b_k + B.b_hasanta + B.b_ss + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('kShm', B.b_k + B.b_hasanta + B.b_ss + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('kxN', B.b_k + B.b_hasanta + B.b_ss + B.b_hasanta + B.b_nn) is True:
            return
        if self.cnv('kxm', B.b_k + B.b_hasanta + B.b_ss + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('kkh', B.b_k + B.b_hasanta + B.b_ss) is True:
            return
        if self.cnv('kSh', B.b_k + B.b_hasanta + B.b_ss) is True:
            return
        if self.cnv('ksh', B.b_k + B.b_sh) is True:
            return
        if self.cnv('kx', B.b_k + B.b_hasanta + B.b_ss) is True:
            return
        if self.cnv('kk', B.b_k + B.b_hasanta + B.b_k) is True:
            return
        if self.cnv('kT', B.b_k + B.b_hasanta + B.b_tt) is True:
            return
        if self.cnv('kt', B.b_k + B.b_hasanta + B.b_t) is True:
            return
        if self.cnv('km', B.b_k + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('kl', B.b_k + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('ks', B.b_k + B.b_hasanta + B.b_s) is True:
            return
        if self.cnv('kh', B.b_kh) is True:
            return
        if self.cnv('k', B.b_k) is True:
            return

    def l(self):
        if self.cnv('lbh', B.b_l + B.b_hasanta + B.b_bh) is True:
            return
        if self.cnv('ldh', B.b_l + B.b_hasanta + B.b_dh) is True:
            return
        if self.cnv('lkh', B.b_l + B.b_kh) is True:
            return
        if self.cnv('lgh', B.b_l + B.b_gh) is True:
            return
        if self.cnv('lph', B.b_l + B.b_ph) is True:
            return
        if self.cnv('lk', B.b_l + B.b_hasanta + B.b_k) is True:
            return
        if self.cnv('lg', B.b_l + B.b_hasanta + B.b_g) is True:
            return
        if self.cnv('lT', B.b_l + B.b_hasanta + B.b_tt) is True:
            return
        if self.cnv('lD', B.b_l + B.b_hasanta + B.b_dd) is True:
            return
        if self.cnv('lp', B.b_l + B.b_hasanta + B.b_p) is True:
            return
        if self.cnv('lv', B.b_l + B.b_hasanta + B.b_bh) is True:
            return
        if self.cnv('lm', B.b_l + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('ll', B.b_l + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('lb', B.b_l + B.b_hasanta + B.b_b) is True:
            return
        if self.cnv('l', B.b_l) is True:
            return

    def m(self):
        if self.cnv('mth', B.b_m + B.b_hasanta + B.b_th) is True:
            return
        if self.cnv('mph', B.b_m + B.b_hasanta + B.b_ph) is True:
            return
        if self.cnv('mbh', B.b_m + B.b_hasanta + B.b_bh) is True:
            return
        if self.cnv('mpl', B.b_m + B.b_p + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('mn', B.b_m + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('mp', B.b_m + B.b_hasanta + B.b_p) is True:
            return
        if self.cnv('mv', B.b_m + B.b_hasanta + B.b_bh) is True:
            return
        if self.cnv('mm', B.b_m + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('ml', B.b_m + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('mb', B.b_m + B.b_hasanta + B.b_b) is True:
            return
        if self.cnv('mf', B.b_m + B.b_hasanta + B.b_ph) is True:
            return
        if self.cnv('m', B.b_m) is True:
            return

    def n(self):
        if self.cnv('NgkSh', B.b_nga + B.b_hasanta + B.b_k + B.b_hasanta + B.b_ss) is True:
            return
        if self.cnv('Ngkkh', B.b_nga + B.b_hasanta + B.b_k + B.b_hasanta + B.b_ss) is True:
            return
        if self.cnv('NGch', B.b_nya + B.b_hasanta + B.b_ch) is True:
            return
        if self.cnv('Nggh', B.b_nga + B.b_hasanta + B.b_gh) is True:
            return
        if self.cnv('Ngkh', B.b_nga + B.b_hasanta + B.b_kh) is True:
            return
        if self.cnv('NGjh', B.b_nya + B.b_hasanta + B.b_jh) is True:
            return
        if self.cnv('ngOU', B.b_nga + B.b_hasanta + B.b_g + B.b_oukar) is True:
            return
        if self.cnv('ngOI', B.b_nga + B.b_hasanta + B.b_g + B.b_oikar) is True:
            return
        if self.cnv('Ngkx', B.b_nga + B.b_hasanta + B.b_k + B.b_hasanta + B.b_ss) is True:
            return
        if self.cnv('NGc', B.b_nya + B.b_hasanta + B.b_c) is True:
            return
        if self.cnv('nch', B.b_nya + B.b_hasanta + B.b_ch) is True:
            return
        if self.cnv('njh', B.b_nya + B.b_hasanta + B.b_jh) is True:
            return
        if self.cnv('ngh', B.b_nga + B.b_hasanta + B.b_gh) is True:
            return
        if self.cnv('Ngk', B.b_nga + B.b_hasanta + B.b_k) is True:
            return
        if self.cnv('Ngx', B.b_nga + B.b_hasanta + B.b_ss) is True:
            return
        if self.cnv('Ngg', B.b_nga + B.b_hasanta + B.b_g) is True:
            return
        if self.cnv('Ngm', B.b_nga + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('NGj', B.b_nya + B.b_hasanta + B.b_j) is True:
            return
        if self.cnv('ndh', B.b_n + B.b_hasanta + B.b_dh) is True:
            return
        if self.cnv('nTh', B.b_n + B.b_hasanta + B.b_tth) is True:
            return
        if self.cnv('NTh', B.b_nn + B.b_hasanta + B.b_tth) is True:
            return
        if self.cnv('nth', B.b_n + B.b_hasanta + B.b_th) is True:
            return
        if self.cnv('nkh', B.b_nga + B.b_hasanta + B.b_kh) is True:
            return
        if self.cnv('ngo', B.b_nga + B.b_hasanta + B.b_g) is True:
            return
        if self.cnv('nga', B.b_nga + B.b_hasanta + B.b_g + B.b_aakar) is True:
            return
        if self.cnv('ngi', B.b_nga + B.b_hasanta + B.b_g + B.b_ikar) is True:
            return
        if self.cnv('ngI', B.b_nga + B.b_hasanta + B.b_g + B.b_iikar) is True:
            return
        if self.cnv('ngu', B.b_nga + B.b_hasanta + B.b_g + B.b_ukar) is True:
            return
        if self.cnv('ngU', B.b_nga + B.b_hasanta + B.b_g + B.b_uukar) is True:
            return
        if self.cnv('nge', B.b_nga + B.b_hasanta + B.b_g + B.b_ekar) is True:
            return
        if self.cnv('ngO', B.b_nga + B.b_hasanta + B.b_g + B.b_okar) is True:
            return
        if self.cnv('NDh', B.b_nn + B.b_hasanta + B.b_ddh) is True:
            return
        if self.cnv('nsh', B.b_n + B.b_sh) is True:
            return
        if self.cnv('Ngr', B.b_nga + B.b_r) is True:
            return
        if self.cnv('NGr', B.b_nya + B.b_r) is True:
            return
        if self.cnv('ngr', B.b_anushar + B.b_r) is True:
            return
        if self.cnv('nj', B.b_nya + B.b_hasanta + B.b_j) is True:
            return
        if self.cnv('Ng', B.b_nga) is True:
            return
        if self.cnv('NG', B.b_nya) is True:
            return
        if self.cnv('nk', B.b_nga + B.b_hasanta + B.b_k) is True:
            return
        if self.cnv('ng', B.b_anushar) is True:
            return
        if self.cnv('nn', B.b_n + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('NN', B.b_nn + B.b_hasanta + B.b_nn) is True:
            return
        if self.cnv('Nn', B.b_nn + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('nm', B.b_n + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('Nm', B.b_nn + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('nd', B.b_n + B.b_hasanta + B.b_d) is True:
            return
        if self.cnv('nT', B.b_n + B.b_hasanta + B.b_tt) is True:
            return
        if self.cnv('NT', B.b_nn + B.b_hasanta + B.b_tt) is True:
            return
        if self.cnv('nD', B.b_n + B.b_hasanta + B.b_dd) is True:
            return
        if self.cnv('ND', B.b_nn + B.b_hasanta + B.b_dd) is True:
            return
        if self.cnv('nt', B.b_n + B.b_hasanta + B.b_t) is True:
            return
        if self.cnv('ns', B.b_n + B.b_hasanta + B.b_s) is True:
            return
        if self.cnv('nc', B.b_nya + B.b_hasanta + B.b_c) is True:
            return
        if self.cnv('n', B.b_n) is True:
            return
        if self.cnv('N', B.b_nn) is True:
            return

    def p(self):
        if self.cnv('phl', B.b_ph + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('pT', B.b_p + B.b_hasanta + B.b_tt) is True:
            return
        if self.cnv('pt', B.b_p + B.b_hasanta + B.b_t) is True:
            return
        if self.cnv('pn', B.b_p + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('pp', B.b_p + B.b_hasanta + B.b_p) is True:
            return
        if self.cnv('pl', B.b_p + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('ps', B.b_p + B.b_hasanta + B.b_s) is True:
            return
        if self.cnv('ph', B.b_ph) is True:
            return
        if self.cnv('fl', B.b_ph + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('f', B.b_ph) is True:
            return
        if self.cnv('p', B.b_p) is True:
            return

    def s(self):
        if self.cnv('shch', B.b_sh + B.b_hasanta + B.b_ch) is True:
            return
        if self.cnv('ShTh', B.b_ss + B.b_hasanta + B.b_tth) is True:
            return
        if self.cnv('Shph', B.b_ss + B.b_hasanta + B.b_ph) is True:
            return
        if self.cnv('Sch', B.b_sh + B.b_hasanta + B.b_ch) is True:
            return
        if self.cnv('skl', B.b_s + B.b_hasanta + B.b_k + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('skh', B.b_s + B.b_hasanta + B.b_kh) is True:
            return
        if self.cnv('sth', B.b_s + B.b_hasanta + B.b_th) is True:
            return
        if self.cnv('sph', B.b_s + B.b_hasanta + B.b_ph) is True:
            return
        if self.cnv('shc', B.b_sh + B.b_hasanta + B.b_c) is True:
            return
        if self.cnv('sht', B.b_sh + B.b_hasanta + B.b_t) is True:
            return
        if self.cnv('shn', B.b_sh + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('shm', B.b_sh + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('shl', B.b_sh + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('Shk', B.b_ss + B.b_hasanta + B.b_k) is True:
            return
        if self.cnv('ShT', B.b_ss + B.b_hasanta + B.b_tt) is True:
            return
        if self.cnv('ShN', B.b_ss + B.b_hasanta + B.b_nn) is True:
            return
        if self.cnv('Shp', B.b_ss + B.b_hasanta + B.b_p) is True:
            return
        if self.cnv('Shf', B.b_ss + B.b_hasanta + B.b_ph) is True:
            return
        if self.cnv('Shm', B.b_ss + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('spl', B.b_s + B.b_hasanta + B.b_p + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('sk', B.b_s + B.b_hasanta + B.b_k) is True:
            return
        if self.cnv('Sc', B.b_sh + B.b_hasanta + B.b_c) is True:
            return
        if self.cnv('sT', B.b_s + B.b_hasanta + B.b_tt) is True:
            return
        if self.cnv('st', B.b_s + B.b_hasanta + B.b_t) is True:
            return
        if self.cnv('sn', B.b_s + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('sp', B.b_s + B.b_hasanta + B.b_p) is True:
            return
        if self.cnv('sf', B.b_s + B.b_hasanta + B.b_ph) is True:
            return
        if self.cnv('sm', B.b_s + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('sl', B.b_s + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('sh', B.b_sh) is True:
            return
        if self.cnv('Sc', B.b_sh + B.b_hasanta + B.b_c) is True:
            return
        if self.cnv('St', B.b_sh + B.b_hasanta + B.b_t) is True:
            return
        if self.cnv('Sn', B.b_sh + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('Sm', B.b_sh + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('Sl', B.b_sh + B.b_hasanta + B.b_l) is True:
            return
        if self.cnv('Sh', B.b_ss) is True:
            return
        if self.cnv('s', B.b_s) is True:
            return
        if self.cnv('S', B.b_sh) is True:
            return

    def t_up(self):
        if self.cnv('tth', B.b_t + B.b_hasanta + B.b_th) is True:
            return
        if self.cnv('t``', B.b_khandatta) is True:
            return
        if self.cnv('TT', B.b_tt + B.b_hasanta + B.b_tt) is True:
            return
        if self.cnv('Tm', B.b_tt + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('Th', B.b_tth) is True:
            return
        if self.cnv('tn', B.b_t + B.b_hasanta + B.b_n) is True:
            return
        if self.cnv('tm', B.b_t + B.b_hasanta + B.b_m) is True:
            return
        if self.cnv('th', B.b_th) is True:
            return
        if self.cnv('tt', B.b_t + B.b_hasanta + B.b_t) is True:
            return
        if self.cnv('T', B.b_tt) is True:
            return
        if self.cnv('t', B.b_t) is True:
            return

    def o_up(self):
        if self.cnv('OI`', B.b_oikar) is True:
            return
        if self.cnv('OU`', B.b_oukar) is True:
            return
        if self.cnv('O`', B.b_okar) is True:
            return
        if (self.consonent(self.prev_t()) is False) or (self.begining() is True):
            if self.cnv('OI', B.b_oi) is True:
                return
            if self.cnv('OU', B.b_ou) is True:
                return
            if self.cnv('O', B.b_o) is True:
                return
        else:
            if self.cnv('OI', B.b_oikar) is True:
                return
            if self.cnv('OU', B.b_oukar) is True:
                return
            if self.cnv('O', B.b_okar) is True:
                return

    def r_up(self):
        if self.next_tex(1, 2) == '`':
            if self.cnv('rri', B.b_rrikar) is True:
                return
        if self.consonent(self.prev_t()) is False:
            if self.cnv('rri', B.b_rri) is True:
                return
        elif self.begining() is True:
            if self.cnv('rri', B.b_rri) is True:
                return
        else:
            if self.cnv('rri', B.b_rrikar) is True:
                return
        if (self.consonent(self.prev_t()) is False) and (self.vowel(self.next_tex(1, 1)) is False) and (self.next_tex(1, 1) != 'r') and (self.next_tex(1, 1) != ''):
            if self.cnv('rr', B.b_r + B.b_hasanta) is True:
                return
        if self.cnv('Rg', B.b_rr + B.b_hasanta + B.b_g) is True:
            return
        if self.cnv('Rh', B.b_rrh) is True:
            return
        if (self.consonent(self.prev_t()) is True) and (self.prev_t() != 'r') and (self.prev_t() != 'y') and (self.prev_t() != 'w') and (self.prev_t() != 'x') and (self.prev_t() != 'Z'):
            if self.cnv('r', B.b_hasanta + B.b_r) is True:
                return
        else:
            if self.cnv('r', B.b_r) is True:
                return
        if self.cnv('R', B.b_rr) is True:
            return

    def small_o(self):
        if ((self.consonent(self.prev_t()) is False) or (self.begining() is True)) and (self.next_t() != '`'):
            if self.cnv('oo', B.b_u) is True:
                return
            if self.cnv('oZ', B.b_a + B.b_hasanta + B.b_z) is True:
                return
            if (self.vowel(self.prev_t()) is True) and (self.prev_t() != 'o'):
                if self.cnv('o', B.b_o) is True:
                    return
            elif self.cnv('o', B.b_a) is True:
                return
        if self.cnv('oo', B.b_ukar) is True:
            return
        if self.cnv('o`', '') is True:
            return
        if self.cnv('o', '') is True:
            return

    def dot(self):
        if self.cnv('...', '...') is True:
            return
        if self.cnv('.`', '.') is True:
            return
        if self.cnv('..', B.b_dari + B.b_dari) is True:
            return
        if self.number(self.next_t()) is True:
            if self.cnv('.', '.') is True:
                return
        elif self.cnv('.', B.b_dari) is True:
            return

    def _my_convert(self):
        self.ln = len(self.text)
        self.pos = 1
        self.rs = ""
        if self.ln == 0:
            return ""
        while True:
            tt = self._mid(self.text, self.pos, 1)
            nt = self.next_t
            pt = self.prev_t
            if tt in "0123456789":
                self.add_rs(B.b_0[:0] + chr(0x09E6 + int(tt)))
            elif tt == "o":
                self.small_o()
            elif tt in ("a", "A"):
                if nt() == "Z":
                    self.add_rs_ex(B.b_a + B.b_hasanta + B.b_z + B.b_aakar, 2)
                elif self.begining() and nt() != "`":
                    self.add_rs(B.b_aa)
                elif (not self.consonent(pt())) and pt() != "a" and nt() != "`":
                    self.add_rs(B.b_y + B.b_aakar)
                elif nt() == "`":
                    self.add_rs_ex(B.b_aakar, 2)
                elif pt() == "a" and nt() != "`":
                    self.add_rs(B.b_aa)
                else:
                    self.add_rs(B.b_aakar)
            elif tt in ("i", "I", "u", "U"):
                ind, kar = {"i": (B.b_i, B.b_ikar), "I": (B.b_ii, B.b_iikar),
                            "u": (B.b_u, B.b_ukar), "U": (B.b_uu, B.b_uukar)}[tt]
                if ((not self.consonent(pt())) or self.begining()) and nt() != "`":
                    self.add_rs(ind)
                elif nt() == "`":
                    self.add_rs_ex(kar, 2)
                else:
                    self.add_rs(kar)
            elif tt in ("e", "E"):
                if ((not self.consonent(pt())) or self.begining()) and nt() != "`":
                    if nt() == "e":
                        self.add_rs_ex(B.b_ii, 2)
                    else:
                        self.add_rs(B.b_e)
                elif nt() == "`":
                    self.add_rs_ex(B.b_ekar, 2)
                else:
                    if nt() == "e":
                        self.add_rs_ex(B.b_iikar, 2)
                    else:
                        self.add_rs(B.b_ekar)
            elif tt == "O":
                self.o_up()
            elif tt == "k":
                self.k()
            elif tt in ("G", "g"):
                self.g()
            elif tt in ("N", "n"):
                self.n()
            elif tt == "c":
                self.c()
            elif tt in ("J", "j"):
                self.j_up()
            elif tt in ("T", "t"):
                self.t_up()
            elif tt in ("D", "d"):
                self.d()
            elif tt in ("p", "f"):
                self.p()
            elif tt in ("b", "v"):
                self.b()
            elif tt == "m":
                self.m()
            elif tt == "z":
                self.add_rs(B.b_z)
            elif tt == "Z":
                self._ya_phala()
            elif tt in ("R", "r"):
                self.r_up()
            elif tt == "l":
                self.l()
            elif tt in ("S", "s"):
                self.s()
            elif tt == "h":
                self.h()
            elif tt == "y":
                if (not self.consonent(pt())) and not self.begining():
                    self.add_rs(B.b_y)
                elif self.begining():
                    self.add_rs(B.b_i + B.b_y)
                else:
                    self._ya_phala(force_plain=True)
            elif tt == "Y":
                self.add_rs(B.b_y)
            elif tt == "w":
                if self.begining() and self.vowel(nt()):
                    self.add_rs(B.b_o + B.b_y)
                elif self.consonent(pt()):
                    self.add_rs(B.b_hasanta + B.b_b)
                else:
                    self.add_rs(B.b_o)
            elif tt == "q":
                self.add_rs(B.b_k)
            elif tt == "x":
                if self.begining():
                    self.add_rs(B.b_e + B.b_k + B.b_hasanta + B.b_s)
                else:
                    self.add_rs(B.b_k + B.b_hasanta + B.b_s)
            elif tt == ".":
                self.dot()
            elif tt == ":":
                if nt() != "`":
                    self.add_rs(B.b_bisharga)
                else:
                    self.add_rs_ex(":", 2)
            elif tt == "^":
                if nt() != "`":
                    self.add_rs(B.b_chandra)
                else:
                    self.add_rs_ex("^", 2)
            elif tt == ",":
                if nt() == ",":
                    self.add_rs_ex(B.b_hasanta + B.zwnj, 2)
                else:
                    self.add_rs(",")
            elif tt == "$":
                self.add_rs(B.b_taka)
            elif tt == "`":
                self.pos += 1
            else:
                self.add_rs(tt)
            if self.pos > self.ln:
                break
        return self.rs

    def _ya_phala(self, force_plain=False):
        pt = self.prev_t()
        if pt == "r":
            p2 = self.prev_tex(2)
            if self.consonent(p2) and p2 not in ("r", "y", "w", "x"):
                self.add_rs(B.b_hasanta + B.b_z)
            else:
                self.add_rs(B.zwj + B.b_hasanta + B.b_z)
        else:
            self.add_rs(B.b_hasanta + B.b_z)


_default = None


def convert(text, autocorrect=True, jo_nukta=False):
    """Convert one Avro-phonetic word to Bangla (module-level convenience)."""
    global _default
    if _default is None:
        _default = EnglishToBangla(True, jo_nukta, AutoCorrect())
    _default.autocorrect = autocorrect
    _default.jo_nukta = "YES" if jo_nukta else "NO"
    return _default.convert(text)


class Dictionary:
    """Bangla word list (Database.db3) for suggestions; loaded lazily."""

    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Database.db3")
        self._words = None
        self._suffix = None

    def _load(self):
        if self._words is not None:
            return
        words = set()
        try:
            con = sqlite3.connect(self.path)
            for (t,) in con.execute("select name from sqlite_master where type='table'").fetchall():
                if t in ("Suffix", "Khandatta"):
                    continue
                words.update(w for (w,) in con.execute('select Words from "%s"' % t) if w)
            con.close()
        except Exception:
            pass
        self._words = sorted(words)

    def suggest(self, bangla_prefix, limit=10):
        self._load()
        if not bangla_prefix:
            return []
        i = bisect.bisect_left(self._words, bangla_prefix)
        res = []
        while i < len(self._words) and self._words[i].startswith(bangla_prefix) and len(res) < 400:
            res.append(self._words[i])
            i += 1
        res.sort(key=lambda w: (len(w), w))
        return res[:limit]


def suggestions(word, limit=8, dictionary=None):
    """Candidate list for a typed Latin word: [converted word, dictionary words starting with it]."""
    conv = convert(word)
    out = [conv]
    d = dictionary or _get_dict()
    for w in d.suggest(conv, limit + 2):
        if w not in out:
            out.append(w)
    return out[:limit]


_dict = None


def _get_dict():
    global _dict
    if _dict is None:
        _dict = Dictionary()
    return _dict
