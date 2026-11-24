"""Tray icon with a menu to open the tools (AppIndicator when available, else Gtk.StatusIcon)."""
import subprocess
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .common import show_about  # noqa: E402

COMMANDS = [("Settings", "settings"), ("Layout viewer", "viewer"), ("Unicode to Bijoy", "convert"),
            ("Spell checker", "spell")]


def _run(sub):
    try:
        subprocess.Popen(["popy-keyboard", sub])
    except OSError:
        subprocess.Popen([sys.executable, "-m", "avrokb.gui.launcher", sub])


def _menu():
    m = Gtk.Menu()
    for label, sub in COMMANDS:
        it = Gtk.MenuItem(label=label)
        it.connect("activate", lambda _w, s=sub: _run(s))
        m.append(it)
    about = Gtk.MenuItem(label="About")
    about.connect("activate", lambda *_: show_about())
    m.append(about)
    m.append(Gtk.SeparatorMenuItem())
    q = Gtk.MenuItem(label="Quit tray")
    q.connect("activate", lambda *_: Gtk.main_quit())
    m.append(q)
    m.show_all()
    return m


def main():
    menu = _menu()
    ind = None
    for ns in ("AyatanaAppIndicator3", "AppIndicator3"):
        try:
            gi.require_version(ns, "0.1")
            mod = __import__("gi.repository", fromlist=[ns])
            AI = getattr(mod, ns)
            ind = AI.Indicator.new("popy-keyboard", "popy-keyboard", AI.IndicatorCategory.APPLICATION_STATUS)
            ind.set_status(AI.IndicatorStatus.ACTIVE)
            ind.set_menu(menu)
            break
        except (ValueError, ImportError, AttributeError):
            ind = None
    if ind is None:
        icon = Gtk.StatusIcon.new_from_icon_name("popy-keyboard")
        icon.set_tooltip_text("Popy Keyboard")
        icon.connect("popup-menu", lambda i, b, t: menu.popup(None, None, Gtk.StatusIcon.position_menu, i, b, t))
        icon.connect("activate", lambda *_: _run("settings"))
        main._icon = icon
    Gtk.main()
