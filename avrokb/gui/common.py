import os
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gdk, GdkPixbuf, Gtk  # noqa: E402

from .. import config  # noqa: E402

CREDITS = (
    "Avro Keyboard — original by Mehdi Hasan Khan / OmicronLab (MPL-2.0)\n"
    "Popy layout credit: আব্দুল্লাহ আল মামুন (BA/MA English) — mamun995599@gmail.com\n"
    "Linux port (IBus) — version %s" % config.VERSION
)


def data_path(name):
    for base in ("/usr/share/popy-keyboard", config.package_data_dir()):
        p = os.path.join(base, name)
        if os.path.exists(p):
            return p
    return os.path.join(config.package_data_dir(), name)


def pixbuf_from_bytes(data):
    if not data:
        return None
    loader = GdkPixbuf.PixbufLoader()
    try:
        loader.write(data)
        loader.close()
        return loader.get_pixbuf()
    except Exception:
        return None


def show_about(parent=None):
    d = Gtk.AboutDialog(transient_for=parent, modal=True)
    d.set_program_name("Popy Keyboard")
    d.set_version(config.VERSION)
    d.set_comments(CREDITS)
    d.set_license_type(Gtk.License.MPL_2_0)
    d.set_website("https://www.omicronlab.com")
    d.run()
    d.destroy()


def error_dialog(parent, text):
    d = Gtk.MessageDialog(transient_for=parent, modal=True, message_type=Gtk.MessageType.ERROR,
                          buttons=Gtk.ButtonsType.OK, text=text)
    d.run()
    d.destroy()
