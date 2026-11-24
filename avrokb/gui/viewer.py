"""Layout viewer: shows the keyboard picture of the selected layout."""
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .. import config, layouts  # noqa: E402
from .common import data_path, pixbuf_from_bytes  # noqa: E402


class ViewerWindow(Gtk.Window):
    def __init__(self, layout_name=None):
        super().__init__(title="Popy Keyboard — Layout viewer")
        self.set_default_size(1020, 640)
        self.lays = {l.name: l for l in layouts.list_layouts(config.layout_dirs())}
        names = ["Popy"] + sorted(self.lays)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=8)
        self.add(box)
        bar = Gtk.Box(spacing=6)
        box.pack_start(bar, False, False, 0)
        self.combo = Gtk.ComboBoxText()
        for n in names:
            self.combo.append_text(n)
        want = layout_name if layout_name in names else "Popy"
        self.combo.set_active(names.index(want))
        self.combo.connect("changed", lambda *_: self.refresh())
        bar.pack_start(Gtk.Label(label="Layout:"), False, False, 0)
        bar.pack_start(self.combo, False, False, 0)
        self.b1 = Gtk.RadioButton.new_with_label_from_widget(None, "Normal / Shift")
        self.b2 = Gtk.RadioButton.new_with_label_from_widget(self.b1, "AltGr")
        self.b1.connect("toggled", lambda *_: self.refresh())
        bar.pack_start(self.b1, False, False, 12)
        bar.pack_start(self.b2, False, False, 0)
        sw = Gtk.ScrolledWindow()
        sw.set_vexpand(True)
        self.image = Gtk.Image()
        sw.add(self.image)
        box.pack_start(sw, True, True, 0)
        self.info = Gtk.Label(xalign=0)
        self.info.set_line_wrap(True)
        self.info.set_selectable(True)
        box.pack_start(self.info, False, False, 0)
        self.refresh()

    def refresh(self):
        name = self.combo.get_active_text()
        second = self.b2.get_active()
        if name == "Popy":
            self.b1.set_label("Keys")
            self.b2.set_label("Rules")
            pb = pixbuf_from_bytes(open(data_path("popy_rules.png" if second else "popy_keys.png"), "rb").read())
            hires = True      # these charts are drawn at 3x: show them at 1/3 size, crisp on any screen
            self.info.set_text("Popy — phonetic rule-based layout.\nCredit: আব্দুল্লাহ আল মামুন")
        else:
            hires = False
            self.b1.set_label("Normal / Shift")
            self.b2.set_label("AltGr")
            lay = self.lays.get(name)
            data = lay.image_altgr() if second else lay.image_normal()
            pb = pixbuf_from_bytes(data)
            self.info.set_text("%s (v%s) — %s\n%s" % (lay.name, lay.version, lay.developer, lay.comment))
        if hires:
            from gi.repository import Gdk
            self.image.set_from_surface(Gdk.cairo_surface_create_from_pixbuf(pb, 3, None))
        else:
            self.image.set_from_pixbuf(pb)


def main(argv=None):
    import sys
    name = (argv or sys.argv[1:] or [None])[0]
    w = ViewerWindow(name)
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()
