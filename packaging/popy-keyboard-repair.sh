#!/bin/sh
# Popy Keyboard (Linux) - মেরামত/ডায়াগনস্টিক স্ক্রিপ্ট
# বড় সিস্টেম আপগ্রেডের পর কিবোর্ড কাজ না করলে চালান:  sh popy-keyboard-repair.sh
# কোনো ডেটা মোছে না; দরকারি প্যাকেজ ইনস্টল ও IBus রিস্টার্ট করে।

LIB=/usr/lib/popy-keyboard
COMP=/usr/share/ibus/component/popy-keyboard.xml
ok()   { printf '  [ঠিক আছে] %s\n' "$1"; }
bad()  { printf '  [সমস্যা]  %s\n' "$1"; PROBLEMS=$((PROBLEMS+1)); }
PROBLEMS=0
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"

echo "== ১. কিবোর্ড ফাইল আছে কি? =="
[ -d "$LIB/avrokb" ] && ok "$LIB" || bad "$LIB নেই - .deb আবার ইনস্টল করুন (sudo apt install ./popy-keyboard_*.deb)"
[ -f "$COMP" ] && ok "$COMP" || bad "IBus component ফাইল নেই - .deb আবার ইনস্টল করুন"

echo "== ২. দরকারি প্যাকেজ =="
if   command -v apt-get >/dev/null; then PM=apt;    PKGS="python3 python3-gi gir1.2-gtk-3.0 gir1.2-ibus-1.0 ibus"
elif command -v dnf     >/dev/null; then PM=dnf;    PKGS="python3 python3-gobject gtk3 ibus ibus-libs"
elif command -v pacman  >/dev/null; then PM=pacman; PKGS="python python-gobject gtk3 ibus"
elif command -v zypper  >/dev/null; then PM=zypper; PKGS="python3 python3-gobject python3-gobject-Gdk typelib-1_0-Gtk-3_0 ibus typelib-1_0-IBus-1_0"
else PM=""; fi

pycheck() { python3 - <<'PY' 2>&1
import gi
gi.require_version("Gtk","3.0"); gi.require_version("IBus","1.0")
from gi.repository import Gtk, IBus
PY
}
if pycheck >/dev/null; then ok "python3 + GTK3 + IBus বাইন্ডিং"
else
  bad "Python-এর GTK3/IBus বাইন্ডিং পাওয়া যাচ্ছে না, ইনস্টল করার চেষ্টা করছি"
  case "$PM" in
    apt)    $SUDO apt-get update -qq; $SUDO apt-get install -y $PKGS ;;
    dnf)    $SUDO dnf install -y $PKGS ;;
    pacman) $SUDO pacman -S --needed --noconfirm $PKGS ;;
    zypper) $SUDO zypper install -y $PKGS ;;
    *) echo "  অজানা প্যাকেজ ম্যানেজার; হাতে ইনস্টল করুন: python3, PyGObject, GTK3, IBus" ;;
  esac
  pycheck >/dev/null && ok "এখন ঠিক" || { bad "এখনও ঠিক হয়নি। এরর:"; pycheck | tail -5; }
fi
# ঐচ্ছিক
[ "$PM" = apt ] && dpkg -s fonts-noto-core >/dev/null 2>&1 || echo "  (ঐচ্ছিক) বাংলা ফন্ট না থাকলে: sudo apt install fonts-noto-core"

echo "== ৩. ইঞ্জিন কোড লোড হয় কি? =="
if [ -d "$LIB/avrokb" ]; then
  out=$(PYTHONPATH=$LIB python3 -c "import avrokb.popy, avrokb.core; print('ok')" 2>&1)
  [ "$out" = ok ] && ok "ইঞ্জিন মডিউল" || { bad "ইঞ্জিন লোড হয়নি:"; echo "$out" | tail -5; }
  # নতুন Python-এর জন্য পুরনো বাইটকোড ক্যাশ পরিষ্কার
  $SUDO find "$LIB" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
  $SUDO python3 -m compileall -q "$LIB" >/dev/null 2>&1
fi

echo "== ৪. IBus রিস্টার্ট =="
if command -v ibus >/dev/null; then
  ibus write-cache >/dev/null 2>&1       # component ক্যাশ নতুন করে
  ibus restart >/dev/null 2>&1 || ibus-daemon -drx >/dev/null 2>&1
  sleep 2
  if ibus list-engine 2>/dev/null | grep -qi "popy"; then ok "Popy ইঞ্জিন তালিকায় আছে"
  else bad "ইঞ্জিন তালিকায় নেই (লগ আউট/লগ ইন করে আবার চালান)"; fi
else bad "ibus কমান্ড নেই"; fi

echo "== ৫. ইনপুট মেথড পরিবেশ =="
case "${XDG_SESSION_TYPE:-}" in wayland) echo "  Wayland সেশন: কিছু অ্যাপে প্রিডিট স্থান ভুল হতে পারে (IBus-এর সীমা)";; esac
[ -n "$GTK_IM_MODULE$QT_IM_MODULE" ] && echo "  GTK_IM_MODULE=$GTK_IM_MODULE QT_IM_MODULE=$QT_IM_MODULE"
if command -v fcitx5 >/dev/null && pgrep -x fcitx5 >/dev/null; then
  bad "Fcitx5 চলছে - IBus-এর সাথে বিরোধ; Fcitx5 বন্ধ করুন বা IBus বেছে নিন"
fi
echo "  সেটিংস > কিবোর্ড > Input Sources (Mint: Region & Language > Input method) থেকে"
echo "  Bangla > Popy যোগ করুন, না থাকলে এই স্ক্রিপ্টের পর আবার লগ ইন করুন।"

echo
if [ "$PROBLEMS" -eq 0 ]; then echo "সব ঠিক আছে। এখনো না চললে লগ আউট করে লগ ইন করুন।"
else echo "$PROBLEMS টি সমস্যা পাওয়া গেছে - ওপরের বার্তা দেখুন; না মিটলে এই আউটপুট পাঠান।"; fi
