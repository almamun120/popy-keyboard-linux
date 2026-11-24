"""Popy Keyboard settings window."""
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .. import config, layouts  # noqa: E402
from . import common  # noqa: E402


class SettingsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Popy Keyboard %s — Settings" % config.VERSION)
        self.set_default_size(460, 420)
        self.s = config.load()
        self.checks = {}
        nb = Gtk.Notebook(margin=8)
        self.add(nb)

        # --- General
        g = self._page()
        nb.append_page(g, Gtk.Label(label="General"))
        self.layout_combo = Gtk.ComboBoxText()
        self.names = list(config.BUILTIN_LAYOUTS) + [l.name for l in layouts.list_layouts(config.layout_dirs())]
        for n in self.names:
            self.layout_combo.append_text(n)
        cur = self.s["layout"]
        self.layout_combo.set_active(self.names.index(cur) if cur in self.names else 0)
        note0 = Gtk.Label(label="Each layout is its own input method: pick Avro Phonetic, Popy Layout, UniBijoy ... in "
                                 "Settings > Keyboard > Input Sources. The layout below is used only by the generic "
                                 "\'Popy Keyboard (choose layout in settings)\' input method.", xalign=0, wrap=True)
        g.pack_start(note0, False, False, 0)
        self._row(g, "Layout of the generic input method", self.layout_combo)
        self.toggle_combo = Gtk.ComboBoxText()
        for k in config.TOGGLE_KEYS:
            self.toggle_combo.append_text(k)
        tk = self.s["toggle_key"]
        self.toggle_combo.set_active(config.TOGGLE_KEYS.index(tk) if tk in config.TOGGLE_KEYS else 0)
        self._row(g, "Bangla / English switch key", self.toggle_combo)
        self.mode_combo = Gtk.ComboBoxText()
        for k in ("bangla", "english"):
            self.mode_combo.append_text(k)
        self.mode_combo.set_active(0 if self.s["start_mode"] == "bangla" else 1)
        self._row(g, "Start in", self.mode_combo)
        self._check(g, "show_preview", "Show preview window (typed English letters; Avro Phonetic also lists suggestions)")
        self._check(g, "output_ansi", "Output ANSI (Bijoy) text instead of Unicode")
        note = Gtk.Label(label="'Right Win' switches modes when pressed alone (the key never opens the Super menu while selected).",
                         xalign=0, wrap=True)
        g.pack_start(note, False, False, 0)

        # --- Phonetic
        p = self._page()
        nb.append_page(p, Gtk.Label(label="Avro Phonetic"))
        self._check(p, "avro_autocorrect", "Auto-correct (Avro Phonetic)")
        self._check(p, "popy_greedy", "Popy: greedy mode (listed conjuncts join by themselves; off = Shift tap after each conjunct)")
        self._check(p, "popy_autocorrect", "Popy: dictionary auto-correct + suggestions in the preview window")
        self._check(p, "avro_suggestions", "Dictionary suggestions in the preview window (Avro Phonetic only)")
        self._check(p, "jo_nukta", "Capital J = য় (jo with nukta)")

        # --- Fixed
        f = self._page()
        nb.append_page(f, Gtk.Label(label="Fixed layouts"))
        self._check(f, "vowel_formatting", "Automatic vowel forming (kar -> vowel after a vowel/digit)")
        self._check(f, "old_style_reph", "Old style reph (type Reph before the consonant)")
        self._check(f, "fix_chandra", "Automatically fix Chandrabindu order")

        # --- buttons
        bar = Gtk.Box(spacing=6, margin=8)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.remove(nb)
        self.add(outer)
        outer.pack_start(nb, True, True, 0)
        outer.pack_start(bar, False, False, 0)
        for label, cb in (("Layout viewer", self.on_viewer), ("About", lambda *_: common.show_about(self)),
                          ("Apply", self.on_apply), ("OK", self.on_ok)):
            b = Gtk.Button(label=label)
            b.connect("clicked", cb)
            bar.pack_end(b, False, False, 0) if label in ("Apply", "OK") else bar.pack_start(b, False, False, 0)

    def _page(self):
        return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=12)

    def _row(self, page, label, widget):
        r = Gtk.Box(spacing=8)
        r.pack_start(Gtk.Label(label=label, xalign=0), True, True, 0)
        r.pack_start(widget, False, False, 0)
        page.pack_start(r, False, False, 0)

    def _check(self, page, key, label):
        c = Gtk.CheckButton(label=label)
        c.set_active(bool(self.s[key]))
        self.checks[key] = c
        page.pack_start(c, False, False, 0)

    def collect(self):
        s = dict(self.s)
        s["layout"] = self.layout_combo.get_active_text() or s["layout"]
        s["toggle_key"] = self.toggle_combo.get_active_text() or s["toggle_key"]
        s["start_mode"] = self.mode_combo.get_active_text() or "bangla"
        for k, c in self.checks.items():
            s[k] = c.get_active()
        return s

    def on_apply(self, *_):
        self.s = self.collect()
        config.save(self.s)

    def on_ok(self, *_):
        self.on_apply()
        self.destroy()

    def on_viewer(self, *_):
        from .viewer import ViewerWindow
        ViewerWindow(self.layout_combo.get_active_text()).show_all()


def main():
    w = SettingsWindow()
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()
