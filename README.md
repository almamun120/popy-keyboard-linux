# Popy Keyboard for Linux — Mint / Ubuntu / Kali

An IBus input method + GTK3 tools, written in Python.

* **Layouts:** Avro Phonetic (classic), Popy (Android rules: `nng`=ঙ, `nnn`/`qn`=ঞ, `q` for special letters only, only 163 listed conjunct pairs join by themselves — a Shift tap forces a join / independent vowel, dictionary auto-correct + preview suggestions from `popy_words.txt.gz`),
  and every fixed `.avrolayout` (UniBijoy, Probhat, Bornona, National (Jatiya), Avro Easy, Munir Optima).
  Drop extra `.avrolayout` files into `~/.local/share/popy-keyboard/layouts/`.
* **Switch key:** Ctrl+Space, Shift+Space, F12, Right Ctrl or Right Win (alone; never opens the Super menu).
* **Output:** Unicode, or ANSI (Bijoy) text.
* **Tools:** settings, layout viewer, Unicode→Bijoy converter, spell checker, tray menu (`popy-keyboard`).
* Credit for the Popy layout: আব্দুল্লাহ আল মামুন (BA/MA English) — mamun995599@gmail.com

## Install
```
sudo apt install ./popy-keyboard_1.0.0_all.deb     # pulls ibus, python3-gi, GTK3

```
Then add the layouts you want as separate input methods (Avro Phonetic, Popy Layout, UniBijoy, Probhat ...):
Settings → Keyboard → Input Sources → Bengali → **Popy Keyboard**
(Cinnamon/Mint: *System Settings → Keyboard → Input Method* or run `ibus-setup`).
Select an input method and press its *Preferences* button (or run `popy-keyboard-settings`) for the switch key, preview window, ANSI output and other options.

Build the package yourself: `packaging/build_deb.sh 1.0.0`  (needs only `dpkg-deb`).
Run the tests: `python3 -m unittest discover -s tests`.

## Notes
* The word you type is shown as underlined *preedit* text and committed with Space/Enter, so it works
  in every application (Wayland and X11) without surrounding-text support.
* Avro Phonetic suggestions are simplified (dictionary words that start with the converted word).
* Not covered: Layout Editor and Skin Designer (Windows-only tools).

**Popy greedy mode** (Settings → Phonetic, default on): the 163 listed conjuncts join by themselves and Shift is a prefix (`t⇧t` = ত্ত). Off: nothing joins by itself, `r`/`z` are independent and Shift is a postfix after the letter (`km⇧` = ক্ম, `kz⇧` = ক্য, `tot⇧` = ত্ত, `ka⇧` = কআ, `ko⇧` = কঅ).
