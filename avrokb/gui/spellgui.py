"""Spell checker tool."""
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # noqa: E402

from .. import config  # noqa: E402
from ..spell import SpellChecker  # noqa: E402


class SpellWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Avro Spell Checker")
        self.set_default_size(680, 560)
        self.sc = SpellChecker(custom_path=os.path.join(config.user_data_dir(), "custom_words.txt"))
        self.errors = []
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=8)
        self.add(box)
        self.view = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD)
        self.buf = self.view.get_buffer()
        self.tag = self.buf.create_tag("bad", background="#ffcccc", underline=1)
        sw = Gtk.ScrolledWindow(); sw.add(self.view); sw.set_vexpand(True)
        box.pack_start(sw, True, True, 0)
        bar = Gtk.Box(spacing=6)
        for label, cb in (("Check", self.on_check), ("Next error", self.on_next), ("Ignore", self.on_ignore),
                          ("Add to dictionary", self.on_add), ("Replace", self.on_replace)):
            b = Gtk.Button(label=label); b.connect("clicked", cb); bar.pack_start(b, False, False, 0)
        box.pack_start(bar, False, False, 0)
        self.status = Gtk.Label(xalign=0)
        box.pack_start(self.status, False, False, 0)
        self.store = Gtk.ListStore(str)
        self.sugg = Gtk.TreeView(model=self.store, headers_visible=False)
        self.sugg.append_column(Gtk.TreeViewColumn("Suggestions", Gtk.CellRendererText(), text=0))
        sw2 = Gtk.ScrolledWindow(); sw2.add(self.sugg); sw2.set_size_request(-1, 150)
        box.pack_start(sw2, False, False, 0)
        self.cur = None

    def _text(self):
        return self.buf.get_text(self.buf.get_start_iter(), self.buf.get_end_iter(), True)

    def on_check(self, *_):
        self.buf.remove_all_tags(self.buf.get_start_iter(), self.buf.get_end_iter())
        self.errors = self.sc.find_errors(self._text())
        for s, e, _w in self.errors:
            self.buf.apply_tag(self.tag, self.buf.get_iter_at_offset(s), self.buf.get_iter_at_offset(e))
        self.status.set_text("%d unknown word(s)" % len(self.errors))
        self.cur = -1
        self.on_next()

    def on_next(self, *_):
        self.store.clear()
        if not self.errors:
            self.cur = None
            return
        self.cur = (self.cur + 1) % len(self.errors)
        s, e, w = self.errors[self.cur]
        a, b = self.buf.get_iter_at_offset(s), self.buf.get_iter_at_offset(e)
        self.buf.select_range(a, b)
        self.view.scroll_to_iter(a, 0.1, False, 0, 0)
        for x in self.sc.suggest(w):
            self.store.append([x])

    def _drop_current(self):
        s, e, w = self.errors.pop(self.cur)
        self.buf.remove_tag(self.tag, self.buf.get_iter_at_offset(s), self.buf.get_iter_at_offset(e))
        self.cur -= 1
        self.on_check_after_edit()

    def on_check_after_edit(self):
        self.on_next()

    def on_ignore(self, *_):
        if self.cur is not None and self.errors:
            self.sc.ignore(self.errors[self.cur][2]); self._drop_current()

    def on_add(self, *_):
        if self.cur is not None and self.errors:
            self.sc.add_custom(self.errors[self.cur][2]); self._drop_current()

    def on_replace(self, *_):
        sel, it = self.sugg.get_selection().get_selected()
        if it is None or self.cur is None or not self.errors:
            return
        new = self.store[it][0]
        s, e, _w = self.errors[self.cur]
        self.buf.delete(self.buf.get_iter_at_offset(s), self.buf.get_iter_at_offset(e))
        self.buf.insert(self.buf.get_iter_at_offset(s), new)
        GLib.idle_add(self.on_check)


def main():
    w = SpellWindow()
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()
