"""Unicode -> Bijoy (SutonnyMJ / Bijoy 2000 ANSI) converter.

Port of the Delphi clsUnicodeToBijoy2000.pas (Avro Keyboard). Generated tables +
hand-written passes. Deviation: the few hard-coded cp1252 fix-ups at the end of
FinalTouch are unreadable in the source copy (mangled bytes) and are omitted
except the ASCII one (Rz -> Ry).
"""

ZWJ = "\u200d"; ZWNJ = "\u200c"
zwj = ZWJ; zwnj = ZWNJ

assamra = 'ৰ'
assamva = 'ৱ'
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
a_0 = '0'
a_1 = '1'
a_2 = '2'
a_3 = '3'
a_4 = '4'
a_5 = '5'
a_6 = '6'
a_7 = '7'
a_8 = '8'
a_9 = '9'
a_a = 'A'
a_aa = 'Av'
a_aakar = 'v'
a_anushar = 's'
a_b = 'e'
a_b_2h_1 = '^'
a_b_2h_2 = '¡'
a_b_2h_3 = '¦'
a_b_2h_4 = 'Ÿ'
a_b_d = 'ã'
a_b_dh = 'ä'
a_b_j = 'â'
a_bh = 'f'
a_bh_2h = '¢'
a_bh_r = 'å'
a_bh_r_2h = '£'
a_bisharga = 't'
a_c = 'P'
a_c_1h = '”'
a_ch = 'Q'
a_chandra = 'u'
a_d = '`'
a_d_1h_1 = '˜'
a_d_1h_2 = '™'
a_d_b = 'Ø'
a_d_d = 'Ï'
a_d_dh = '×'
a_d_m = 'Ù'
a_dari = '|'
a_dd = 'W'
a_dd_dd = 'Ç'
a_ddh = 'X'
a_dh = 'a'
a_doubledanda = '\\'
a_e = 'G'
a_ekar1 = '†'
a_ekar2 = '‡'
a_enddoublequote = 'Ó'
a_g = 'M'
a_g_d = 'º'
a_g_dh = '»'
a_g_g = '¹'
a_g_ukar = '¸'
a_gh = 'N'
a_h = 'n'
a_h_m = 'þ'
a_h_n = 'ý'
a_h_rrikar = 'ü'
a_h_ukar = 'û'
a_hasanta = '&'
a_i = 'B'
a_ii = 'C'
a_iikar = 'x'
a_ikar = 'w'
a_j = 'R'
a_j_j = '¾'
a_j_jh = 'À'
a_j_nya = 'Á'
a_jh = 'S'
a_k = 'K'
a_k_2h = '‹'
a_k_k = '°'
a_k_m = '´'
a_k_r = 'µ'
a_k_r_2h = 'Œ'
a_k_s = '·'
a_k_ss = '¶'
a_k_ss_m = '²'
a_k_t = '³'
a_k_tt = '±'
a_kh = 'L'
a_khandata = 'r'
a_l = 'j'
a_l_2h_1 = '¬'
a_l_2h_2 = '\xad'
a_l_2h_3 = '−'
a_l_dd = 'ì'
a_l_g = 'ê'
a_l_k = 'é'
a_l_p = 'í'
a_l_ph = 'î'
a_l_tt = 'ë'
a_m = 'g'
a_m_1h = '¤'
a_m_2h_1 = '¥'
a_m_2h_2 = '§'
a_m_n = 'æ'
a_m_ph = 'ç'
a_n = 'b'
a_n_1h_1 = 'š'
a_n_1h_2 = '›'
a_n_dd = 'Û'
a_n_dh = 'Ü'
a_n_s = 'Ý'
a_n_tth = 'Ú'
a_nga = 'O'
a_nga_1h = '•'
a_nga_g = '½'
a_nga_k = '¼'
a_nn = 'Y'
a_nn_2h_1 = 'è'
a_nn_2h_2 = 'œ'
a_nn_dd = 'Ê'
a_nn_tt = 'È'
a_nn_tth = 'É'
a_nya = 'T'
a_nya_c = 'Â'
a_nya_ch = 'Ã'
a_nya_j = 'Ä'
a_nya_jh = 'Å'
a_o = 'I'
a_oi = 'H'
a_oikar1 = 'ˆ'
a_oikar2 = '‰'
a_ou = 'J'
a_oukar = 'Š'
a_p = 'c'
a_p_p = 'à'
a_p_s = 'á'
a_p_t = 'ß'
a_p_tt = 'Þ'
a_ph = 'd'
a_r = 'i'
a_reph = '©'
a_rfola_1 = 'ª'
a_rfola_2 = '«'
a_rfola_3 = 'Ö'
a_rr = 'o'
a_rr_g = 'ÿ'
a_rrh = 'p'
a_rri = 'F'
a_rrikar1 = '„'
a_rrikar2 = '…'
a_s = 'm'
a_s_1h_1 = '¯'
a_s_1h_2 = 'ˉ'
a_s_kh = 'ö'
a_s_n = 'ø'
a_s_ph = 'ù'
a_s_tt = '÷'
a_sh = 'k'
a_sh_c = 'ð'
a_sh_ch = 'ñ'
a_sh_ukar = 'ï'
a_ss = 'l'
a_ss_1h = '®'
a_ss_nn = 'ò'
a_ss_ph = 'õ'
a_ss_tt = 'ó'
a_ss_tth = 'ô'
a_startdoublequote = 'Ò'
a_t = 'Z'
a_t_2h = '—'
a_t_m = 'Í'
a_t_r = 'Î'
a_t_r_2h = '¿'
a_t_t = 'Ë'
a_t_th = 'Ì'
a_t_ukar_2h = '‘'
a_taka = '$'
a_th = '_'
a_th_2h = '’'
a_tt = 'U'
a_tt_tt = 'Æ'
a_tth = 'V'
a_u = 'D'
a_ukar1 = 'z'
a_ukar2 = 'y'
a_ukar3 = '–'
a_ukar4 = '“'
a_uu = 'E'
a_uukar1 = '‚'
a_uukar2 = '~'
a_uukar3 = 'ƒ'
a_y = 'q'
a_z = 'h'
a_zfola = '¨'

def mid(s, start, length):
    """Delphi MidStr (1-based, forgiving)."""
    if start < 1:
        start = 1
    if length <= 0:
        return ""
    return s[start - 1:start - 1 + length]


def stuff(s, start, length, sub):
    return s[:start - 1] + sub + s[start - 1 + length:]


_PURE = set(c for c in (b_b, b_bh, b_c, b_ch, b_d, b_dd, b_ddh, b_dh, b_g, b_gh, b_h, b_j, b_jh, b_k, b_kh, b_l, b_m, b_n,
                        b_nga, b_nn, b_nya, b_p, b_ph, b_r, b_rr, b_rrh, b_s, b_sh, b_ss, b_t, b_th, b_tt, b_tth, b_z, b_y,
                        b_khandatta, assamra, assamva))


def is_pure_cons(ch):
    return ch in _PURE


_BASELINE = set((b_kh, b_g, b_gh, b_nn, b_th, b_d, b_dh, b_n, b_p, b_b, b_m, b_z, b_r, b_l, b_sh, b_ss, b_s, b_h, b_y))


def baseline_right(ch):
    return ch in _BASELINE


def _full_forms(t):
    t = t.replace(b_0, a_0)
    t = t.replace(b_1, a_1)
    t = t.replace(b_2, a_2)
    t = t.replace(b_3, a_3)
    t = t.replace(b_4, a_4)
    t = t.replace(b_5, a_5)
    t = t.replace(b_6, a_6)
    t = t.replace(b_7, a_7)
    t = t.replace(b_8, a_8)
    t = t.replace(b_9, a_9)
    t = t.replace(b_taka, a_taka)
    t = t.replace(b_dari, a_dari)
    t = t.replace('॥', a_doubledanda)
    t = t.replace(b_khandatta, a_khandata)
    t = t.replace(b_anushar, a_anushar)
    t = t.replace(b_bisharga, a_bisharga)
    t = t.replace(b_chandra, a_chandra)
    t = t.replace(b_k + b_hasanta + b_k, a_k_k)
    t = t.replace(b_k + b_hasanta + b_tt, a_k_tt)
    t = t.replace(b_k + b_hasanta + b_ss + b_hasanta + b_m, a_k_ss_m)
    t = t.replace(b_k + b_hasanta + b_t, a_k_t)
    t = t.replace(b_k + b_hasanta + b_m, a_k_m)
    t = t.replace(b_k + b_hasanta + b_ss, a_k_ss)
    t = t.replace(b_k + b_hasanta + b_s, a_k_s)
    t = t.replace(b_g + b_hasanta + b_g, a_g_g)
    t = t.replace(b_g + b_hasanta + b_d, a_g_d)
    t = t.replace(b_g + b_hasanta + b_dh, a_g_dh)
    t = t.replace(b_nga + b_hasanta + b_k, a_nga_k)
    t = t.replace(b_nga + b_hasanta + b_g, a_nga_g)
    t = t.replace(b_j + b_hasanta + b_j, a_j_j)
    t = t.replace(b_j + b_hasanta + b_jh, a_j_jh)
    t = t.replace(b_j + b_hasanta + b_nya, a_j_nya)
    t = t.replace(b_nya + b_hasanta + b_c, a_nya_c)
    t = t.replace(b_nya + b_hasanta + b_ch, a_nya_ch)
    t = t.replace(b_nya + b_hasanta + b_j, a_nya_j)
    t = t.replace(b_nya + b_hasanta + b_jh, a_nya_jh)
    t = t.replace(b_tt + b_hasanta + b_tt, a_tt_tt)
    t = t.replace(b_dd + b_hasanta + b_dd, a_dd_dd)
    t = t.replace(b_nn + b_hasanta + b_tt, a_nn_tt)
    t = t.replace(b_nn + b_hasanta + b_tth, a_nn_tth)
    t = t.replace(b_nn + b_hasanta + b_dd, a_nn_dd)
    t = t.replace(b_t + b_hasanta + b_t, a_t_t)
    t = t.replace(b_t + b_hasanta + b_th, a_t_th)
    t = t.replace(b_t + b_hasanta + b_m, a_t_m)
    t = t.replace(b_d + b_hasanta + b_d, a_d_d)
    t = t.replace(b_d + b_hasanta + b_dh, a_d_dh)
    t = t.replace(b_d + b_hasanta + b_b, a_d_b)
    t = t.replace(b_d + b_hasanta + b_m, a_d_m)
    t = t.replace(b_n + b_hasanta + b_tth, a_n_tth)
    t = t.replace(b_n + b_hasanta + b_dd, a_n_dd)
    t = t.replace(b_n + b_hasanta + b_dh, a_n_dh)
    t = t.replace(b_n + b_hasanta + b_s, a_n_s)
    t = t.replace(b_p + b_hasanta + b_tt, a_p_tt)
    t = t.replace(b_p + b_hasanta + b_t, a_p_t)
    t = t.replace(b_p + b_hasanta + b_p, a_p_p)
    t = t.replace(b_p + b_hasanta + b_s, a_p_s)
    t = t.replace(b_b + b_hasanta + b_j, a_b_j)
    t = t.replace(b_b + b_hasanta + b_d, a_b_d)
    t = t.replace(b_b + b_hasanta + b_dh, a_b_dh)
    t = t.replace(b_m + b_hasanta + b_n, a_m_n)
    t = t.replace(b_m + b_hasanta + b_ph, a_m_ph)
    t = t.replace(b_l + b_hasanta + b_k, a_l_k)
    t = t.replace(b_l + b_hasanta + b_g, a_l_g)
    t = t.replace(b_l + b_hasanta + b_tt, a_l_tt)
    t = t.replace(b_l + b_hasanta + b_dd, a_l_dd)
    t = t.replace(b_l + b_hasanta + b_p, a_l_p)
    t = t.replace(b_l + b_hasanta + b_ph, a_l_ph)
    t = t.replace(b_sh + b_hasanta + b_c, a_sh_c)
    t = t.replace(b_sh + b_hasanta + b_ch, a_sh_ch)
    t = t.replace(b_ss + b_hasanta + b_nn, a_ss_nn)
    t = t.replace(b_ss + b_hasanta + b_tt, a_ss_tt)
    t = t.replace(b_ss + b_hasanta + b_tth, a_ss_tth)
    t = t.replace(b_ss + b_hasanta + b_ph, a_ss_ph)
    t = t.replace(b_s + b_hasanta + b_kh, a_s_kh)
    t = t.replace(b_s + b_hasanta + b_tt, a_s_tt)
    t = t.replace(b_s + b_hasanta + b_n, a_s_n)
    t = t.replace(b_s + b_hasanta + b_ph, a_s_ph)
    t = t.replace(b_h + b_hasanta + b_n, a_h_n)
    t = t.replace(b_h + b_hasanta + b_m, a_h_m)
    t = t.replace(b_rr + b_hasanta + b_g, a_rr_g)
    return t


def _consonants(t):
    t = t.replace(b_k, a_k)
    t = t.replace(b_kh, a_kh)
    t = t.replace(b_g, a_g)
    t = t.replace(b_gh, a_gh)
    t = t.replace(b_nga, a_nga)
    t = t.replace(b_c, a_c)
    t = t.replace(b_ch, a_ch)
    t = t.replace(b_j, a_j)
    t = t.replace(b_jh, a_jh)
    t = t.replace(b_nya, a_nya)
    t = t.replace(b_tt, a_tt)
    t = t.replace(b_tth, a_tth)
    t = t.replace(b_dd, a_dd)
    t = t.replace(b_ddh, a_ddh)
    t = t.replace(b_nn, a_nn)
    t = t.replace(b_t, a_t)
    t = t.replace(b_th, a_th)
    t = t.replace(b_d, a_d)
    t = t.replace(b_dh, a_dh)
    t = t.replace(b_n, a_n)
    t = t.replace(b_p, a_p)
    t = t.replace(b_ph, a_ph)
    t = t.replace(b_b, a_b)
    t = t.replace(b_bh, a_bh)
    t = t.replace(b_m, a_m)
    t = t.replace(b_z, a_z)
    t = t.replace(b_r, a_r)
    t = t.replace(b_l, a_l)
    t = t.replace(b_sh, a_sh)
    t = t.replace(b_ss, a_ss)
    t = t.replace(b_s, a_s)
    t = t.replace(b_h, a_h)
    t = t.replace(b_y, a_y)
    t = t.replace(b_rr, a_rr)
    t = t.replace(b_rrh, a_rrh)
    return t


def _second_half(t):
    t = t.replace(b_hasanta + b_bh, a_bh_2h)
    t = t.replace(b_hasanta + b_t, a_t_2h)
    t = t.replace(b_hasanta + b_th, a_th_2h)
    t = t.replace(b_hasanta + b_k, a_k_2h)
    while True:
        i = t.find(b_hasanta + b_b) + 1
        if i <= 0:
            break
        w = mid(t, i - 1, 1)
        if w in (b_s, b_ss, b_m, b_n, b_d, a_m_1h, a_ss_1h, a_s_1h_1, a_n_1h_1, a_d_1h_2):
            t = stuff(t, i, 2, a_b_2h_1)
        elif w in (b_dh, b_b, b_h):
            t = stuff(t, i, 2, a_b_2h_4)
        elif w in (b_sh, b_g, b_p):
            t = stuff(t, i, 2, a_b_2h_3)
        else:
            t = stuff(t, i, 2, a_b_2h_2)
    while True:
        i = t.find(b_hasanta + b_m) + 1
        if i <= 0:
            break
        w = mid(t, i - 1, 1)
        if w in (a_m_1h, a_ss_1h, a_c_1h, a_s_1h_1, a_d_1h_2, a_n_1h_1, a_n_1h_2):
            t = stuff(t, i, 2, a_m_2h_2)
        elif w == a_nga_1h:
            t = stuff(t, i, 2, a_m)
        else:
            t = stuff(t, i, 2, a_m_2h_1)
    while True:
        i = t.find(b_hasanta + b_l) + 1
        if i <= 0:
            break
        w = mid(t, i - 1, 1)
        t = stuff(t, i, 2, a_l_2h_3 if baseline_right(w) else a_l_2h_1)
    t = t.replace(b_hasanta + b_nn, a_nn_2h_1)
    t = t.replace(b_hasanta + b_n, a_nn_2h_2)
    return t


def _first_half(t):
    t = t.replace(b_m + b_hasanta, a_m_1h + b_hasanta)
    t = t.replace(b_ss + b_hasanta, a_ss_1h + b_hasanta)
    t = t.replace(b_c + b_hasanta, a_c_1h + b_hasanta)
    t = t.replace(b_nga + b_hasanta, a_nga_1h + b_hasanta)
    t = t.replace(b_s + b_hasanta, a_s_1h_1 + b_hasanta)
    while True:
        i = t.find(b_d + b_hasanta) + 1
        if i <= 0:
            break
        rep = a_d_1h_1 if mid(t, i + 2, 1) == b_g else a_d_1h_2
        t = t[:i - 1] + rep + t[i:]
    while True:
        i = t.find(b_n + b_hasanta) + 1
        if i <= 0:
            break
        nx = mid(t, i + 2, 1)
        if nx in (b_t, b_th, b_l, b_b, a_t_r_2h, a_t_ukar_2h):
            rep = a_n_1h_1
        elif nx in (b_m, b_n):
            rep = a_n
        else:
            rep = a_n_1h_2
        t = t[:i - 1] + rep + t[i:]
    return t


def _rfola_zfola_hasanta(t):
    t = t.replace(b_hasanta + b_z, a_zfola)
    t = t.replace(b_hasanta + zwnj, a_hasanta)
    while True:
        i = t.find(b_hasanta + b_r) + 1
        if i <= 0:
            break
        p = mid(t, i - 1, 1)
        if p in (b_p, b_g):
            t = stuff(t, i, 2, a_rfola_3)
        elif p == b_bh:
            if mid(t, i - 2, 1) == b_hasanta:
                t = stuff(t, i - 1, 3, a_bh_r_2h)
            else:
                t = stuff(t, i - 1, 3, a_bh_r)
        elif p == b_k:
            if mid(t, i - 2, 1) == b_hasanta:
                t = stuff(t, i - 1, 3, a_k_r_2h)
            else:
                t = stuff(t, i - 1, 3, a_k_r)
        elif p == b_t:
            if mid(t, i - 2, 1) == b_hasanta:
                if mid(t, i - 3, 1) in (b_k, b_t):
                    t = stuff(t, i, 2, a_rfola_2)
                else:
                    t = stuff(t, i - 1, 3, a_t_r_2h)
            else:
                t = stuff(t, i - 1, 3, a_t_r)
        else:
            if p == b_ph:
                t = stuff(t, i, 2, a_rfola_2)
            else:
                t = stuff(t, i, 2, a_rfola_1)
    return t


def _denormalize(u):
    t = u.replace(b_z + b_nukta, b_y)
    t = t.replace(b_dd + b_nukta, b_rr)
    t = t.replace(b_ddh + b_nukta, b_rrh)
    return t


def _rearrange_kars(t):
    t = t.replace(b_okar, b_ekar + b_aakar)
    t = t.replace(b_oukar, b_ekar + b_lengthmark)
    movable = (b_ekar, b_ikar, b_oikar)
    if not t:
        return t
    i = len(t)
    acc = ""
    kar = ""
    while True:
        ch = t[i - 1]
        if ch in movable:
            kar = ch
        else:
            if kar == "":
                acc = ch + acc
            else:
                if i - 1 < 1:
                    acc = kar + ch + acc
                    kar = ""
                else:
                    if (not is_pure_cons(ch)) and ch not in (b_hasanta, zwj, zwnj):
                        acc = ch + kar + acc
                        kar = ""
                    else:
                        if ch in (b_hasanta, zwj, zwnj):
                            acc = ch + acc
                        if is_pure_cons(ch):
                            if t[i - 2] in (b_hasanta, zwj, zwnj):
                                acc = ch + acc
                            else:
                                acc = kar + ch + acc
                                kar = ""
        i -= 1
        if i < 1:
            break
    if kar:  # pending kar never placed (cannot normally happen)
        acc = kar + acc
    t = acc
    t = t.replace("“", a_startdoublequote)
    t = t.replace("”", a_enddoublequote)
    return t


def _rearrange_reph(t):
    if len(t) < 3:
        return t
    n = len(t)
    i = 1
    acc = ""
    pending = False

    def movable(i):
        if i + 2 > n:
            return False
        return t[i - 1] == b_r and t[i] == b_hasanta and t[i + 1] not in (zwj, zwnj)

    while True:
        ch = t[i - 1]
        if not movable(i):
            if not pending:
                acc += ch
            else:
                if (not is_pure_cons(ch)) and ch not in (b_hasanta, zwj, zwnj):
                    acc += a_reph + ch
                    pending = False
                else:
                    if i + 1 > n:
                        acc += ch + a_reph
                        pending = False
                    else:
                        if ch in (b_hasanta, zwj, zwnj):
                            acc += ch
                        if is_pure_cons(ch):
                            if t[i] in (b_hasanta, zwj, zwnj):
                                acc += ch
                            else:
                                acc += ch + a_reph
                                pending = False
        else:
            pending = True
            i += 1
        i += 1
        if i > n:
            break
    return acc


_UR_PREFIX3 = ((b_sh, b_r), (b_d, b_r), (b_g, b_r), (b_t, b_r), (b_j, b_r), (b_th, b_r), (b_dh, b_r),
               (b_p, b_r), (b_b, b_r), (b_bh, b_r), (b_m, b_r), (b_s, b_r))
_UR_PREFIX5 = ((b_n, b_d, b_r), (b_m, b_p, b_r), (b_ss, b_p, b_r), (b_s, b_p, b_r))


def _ra_special(t, i):
    for a, b in _UR_PREFIX3:
        if mid(t, i - 3, 3) == a + b_hasanta + b:
            return True
    for a, b, c in _UR_PREFIX5:
        if mid(t, i - 5, 5) == a + b_hasanta + b + b_hasanta + c:
            return True
    return False


_UL_PREFIX3 = (b_g, b_p, b_b, b_sh, b_s)


def _la_special(t, i):
    for a in _UL_PREFIX3:
        if mid(t, i - 3, 3) == a + b_hasanta + b_l:
            return True
    return mid(t, i - 5, 5) == b_s + b_hasanta + b_p + b_hasanta + b_l


def _setc(t, i, c):
    return t[:i - 1] + c + t[i:]


def _kars_vowels(t):
    ws = (" ", "\r", "\n", "\t")
    while True:
        i = t.find(b_ekar) + 1
        if i <= 0:
            break
        t = _setc(t, i, a_ekar1 if (i == 1 or mid(t, i - 1, 1) in ws) else a_ekar2)
    while True:
        i = t.find(b_oikar) + 1
        if i <= 0:
            break
        t = _setc(t, i, a_oikar1 if (i == 1 or mid(t, i - 1, 1) in ws) else a_oikar2)
    t = t.replace(b_g + b_ukar, a_g_ukar)
    t = t.replace(b_sh + b_ukar, a_sh_ukar)
    t = t.replace(b_h + b_ukar, a_h_ukar)
    t = t.replace(b_hasanta + b_t + b_ukar, b_hasanta + a_t_ukar_2h)
    while True:
        i = t.find(b_ukar) + 1
        if i <= 0:
            break
        if i - 1 >= 1:
            prev = t[i - 2]
            if baseline_right(prev):
                if prev == b_r:
                    if _ra_special(t, i):
                        t = _setc(t, i, a_ukar4)
                    elif mid(t, i - 2, 1) != b_hasanta:
                        t = _setc(t, i, a_ukar4)
                    else:
                        t = _setc(t, i, a_ukar2)
                elif prev == b_l:
                    t = _setc(t, i, a_ukar4 if _la_special(t, i) else a_ukar2)
                else:
                    t = _setc(t, i, a_ukar2)
                if mid(t, i - 3, 3) == b_ss + b_hasanta + b_nn:
                    t = _setc(t, i, a_ukar1)
            else:
                t = _setc(t, i, a_ukar3 if prev in (b_rr, b_rrh) else a_ukar1)
        else:
            t = _setc(t, i, a_ukar1)
    while True:
        i = t.find(b_uukar) + 1
        if i <= 0:
            break
        if i - 1 >= 1:
            prev = t[i - 2]
            if baseline_right(prev):
                if prev == b_r:
                    if _ra_special(t, i):
                        t = _setc(t, i, a_uukar3)
                    elif mid(t, i - 2, 1) != b_hasanta:
                        t = _setc(t, i, a_uukar3)
                    else:
                        t = _setc(t, i, a_uukar2)
                elif prev == b_l:
                    t = _setc(t, i, a_uukar3 if _la_special(t, i) else a_uukar2)
                else:
                    t = _setc(t, i, a_uukar2)
            else:
                t = _setc(t, i, a_uukar1)
        else:
            t = _setc(t, i, a_uukar1)
    t = t.replace(b_h + b_rrikar, a_h_rrikar)
    while True:
        i = t.find(b_rrikar) + 1
        if i <= 0:
            break
        if i - 1 >= 1 and baseline_right(t[i - 2]):
            t = _setc(t, i, a_rrikar1)
        else:
            t = _setc(t, i, a_rrikar2)
    t = t.replace(b_aakar, a_aakar)
    t = t.replace(b_ikar, a_ikar)
    t = t.replace(b_iikar, a_iikar)
    t = t.replace(b_lengthmark, a_oukar)
    for b, a in ((b_a, a_a), (b_aa, a_aa), (b_i, a_i), (b_ii, a_ii), (b_u, a_u), (b_uu, a_uu), (b_rri, a_rri),
                 (b_e, a_e), (b_oi, a_oi), (b_o, a_o), (b_ou, a_ou)):
        t = t.replace(b, a)
    return t


def _final_touch(t):
    t = t.replace(b_hasanta, "").replace(zwj, "").replace(zwnj, "")
    t = t.replace("Rz", "Ry")
    return t


def unicode_to_bijoy(text):
    """Convert Unicode Bangla text to Bijoy (ANSI) text."""
    if not text:
        return ""
    t = _denormalize(text)
    t = _rearrange_kars(t)
    t = _rearrange_reph(t)
    t = _kars_vowels(t)
    t = _rfola_zfola_hasanta(t)
    t = _full_forms(t)
    t = _first_half(t)
    t = _second_half(t)
    t = _consonants(t)
    t = _final_touch(t)
    return t
