#!/bin/sh
# Build popy-keyboard_<ver>_all.deb  (needs only dpkg-deb)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/.."
VER="${1:-1.0.0}"
OUT="${2:-$SRC/dist}"
ROOT="$(mktemp -d)"
LIB="$ROOT/usr/lib/popy-keyboard"
mkdir -p "$LIB" "$ROOT/usr/bin" "$ROOT/usr/share/ibus/component" "$ROOT/usr/share/applications" \
         "$ROOT/usr/share/icons/hicolor/scalable/apps" "$ROOT/DEBIAN" "$OUT"
cp -r "$SRC/avrokb" "$LIB/"
find "$LIB" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
cat > "$LIB/ibus-engine-popy" <<'EOS'
#!/bin/sh
export PYTHONPATH=/usr/lib/popy-keyboard${PYTHONPATH:+:$PYTHONPATH}
exec python3 -m avrokb.ibus_engine "$@"
EOS
cat > "$ROOT/usr/bin/popy-keyboard" <<'EOS'
#!/bin/sh
export PYTHONPATH=/usr/lib/popy-keyboard${PYTHONPATH:+:$PYTHONPATH}
exec python3 -m avrokb.gui.launcher "$@"
EOS
for t in settings:settings viewer:viewer convert:convert spell:spell; do
  n="${t%%:*}"; s="${t##*:}"
  cat > "$ROOT/usr/bin/popy-keyboard-$n" <<EOS
#!/bin/sh
exec /usr/bin/popy-keyboard $s "\$@"
EOS
done
chmod 755 "$LIB/ibus-engine-popy" "$ROOT"/usr/bin/popy-keyboard*
python3 "$HERE/gen_component.py" > "$ROOT/usr/share/ibus/component/popy-keyboard.xml"
cp "$HERE/popy-keyboard.svg" "$ROOT/usr/share/icons/hicolor/scalable/apps/popy-keyboard.svg"
mk_desktop() { # file name exec comment
  cat > "$ROOT/usr/share/applications/$1.desktop" <<EOD
[Desktop Entry]
Type=Application
Name=$2
Exec=$3
Icon=popy-keyboard
Comment=$4
Categories=Utility;Settings;
EOD
}
mk_desktop popy-keyboard-settings "Popy Keyboard Settings" popy-keyboard-settings "Configure Popy Keyboard"
mk_desktop popy-keyboard-converter "Unicode to Bijoy" popy-keyboard-convert "Convert Unicode Bangla to Bijoy"
mk_desktop popy-keyboard-spell "Popy Spell Checker" popy-keyboard-spell "Bangla spell checker"
mk_desktop popy-keyboard-viewer "Popy Layout Viewer" popy-keyboard-viewer "Show keyboard layouts"
SIZE=$(du -sk "$ROOT/usr" | cut -f1)
cat > "$ROOT/DEBIAN/control" <<EOC
Package: popy-keyboard
Version: $VER
Section: utils
Priority: optional
Architecture: all
Installed-Size: $SIZE
Replaces: avro-keyboard
Conflicts: avro-keyboard
Provides: avro-keyboard
Depends: python3 (>= 3.8), python3-gi, gir1.2-gtk-3.0, gir1.2-ibus-1.0, ibus
Recommends: gir1.2-ayatanaappindicator3-0.1, fonts-noto-core
Maintainer: Popy Keyboard Linux port <noreply@example.com>
Homepage: https://www.omicronlab.com
Description: Popy Keyboard for Linux - Bangla input method (IBus)
 Avro Phonetic, Popy phonetic layout and fixed layouts (UniBijoy, Probhat,
 Bornona, National, Avro Easy, Munir Optima), with a settings GUI, layout
 viewer, Unicode to Bijoy converter and spell checker.
EOC
cat > "$ROOT/DEBIAN/postinst" <<'EOC'
#!/bin/sh
set -e
python3 -m compileall -q /usr/lib/popy-keyboard >/dev/null 2>&1 || true
gtk-update-icon-cache -q /usr/share/icons/hicolor >/dev/null 2>&1 || true
exit 0
EOC
chmod 755 "$ROOT/DEBIAN/postinst"
dpkg-deb --root-owner-group --build "$ROOT" "$OUT/popy-keyboard_${VER}_all.deb"
rm -rf "$ROOT"
echo "built $OUT/popy-keyboard_${VER}_all.deb"
