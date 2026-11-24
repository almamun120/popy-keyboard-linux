"""Unicode -> Bijoy (ANSI) converter tool."""
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

from ..bijoy import unicode_to_bijoy  # noqa: E402


class ConverterWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Unicode to Bijoy")
        self.set_default_size(640, 520)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=8)
        self.add(box)
        box.pack_start(Gtk.Label(label="Unicode text:", xalign=0), False, False, 0)
        self.src = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD)
        sw1 = Gtk.ScrolledWindow(); sw1.add(self.src)
        box.pack_start(sw1, True, True, 0)
        bar = Gtk.Box(spacing=6)
        b = Gtk.Button(label="Convert ▼"); b.connect("clicked", self.on_convert)
        c = Gtk.Button(label="Copy result"); c.connect("clicked", self.on_copy)
        bar.pack_start(b, False, False, 0); bar.pack_start(c, False, False, 0)
        box.pack_start(bar, False, False, 0)
        box.pack_start(Gtk.Label(label="Bijoy (ANSI) text — use a Bijoy font such as SutonnyMJ to read it:", xalign=0), False, False, 0)
        self.dst = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD)
        sw2 = Gtk.ScrolledWindow(); sw2.add(self.dst)
        box.pack_start(sw2, True, True, 0)

    @staticmethod
    def _get(view):
        buf = view.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)

    def on_convert(self, *_):
        self.dst.get_buffer().set_text(unicode_to_bijoy(self._get(self.src)))

    def on_copy(self, *_):
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(self._get(self.dst), -1)


def main():
    w = ConverterWindow()
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()
