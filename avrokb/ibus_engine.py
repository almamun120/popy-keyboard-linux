"""IBus engine for Popy Keyboard.  Started by IBus via
/usr/lib/popy-keyboard/ibus-engine-popy --ibus   (see data/popy-keyboard.xml)."""
import os
import subprocess
import sys

import gi

gi.require_version("IBus", "1.0")
from gi.repository import GLib, GObject, IBus  # noqa: E402

from . import config  # noqa: E402
from .core import Mods, TypingCore  # noqa: E402

ENGINE_NAME = "popy-keyboard"
M = IBus.ModifierType


def _text(s, underline=False):
    t = IBus.Text.new_from_string(s)
    if underline and s:
        t.append_attribute(IBus.AttrType.UNDERLINE, IBus.AttrUnderline.SINGLE, 0, len(s))
    return t


class AvroEngine(IBus.Engine):
    __gtype_name__ = "AvroKeyboardEngine"

    def __init__(self, bus, object_path, engine_name=ENGINE_NAME):
        super().__init__(engine_name=engine_name, connection=bus.get_connection(), object_path=object_path)
        self.core = TypingCore(engine_name=engine_name)
        if self.core.kind == "popy":
            import threading
            from . import popy_dict
            threading.Thread(target=popy_dict.get().load, daemon=True).start()   # ~1 s, keep typing snappy
        self._cfg_mtime = config.mtime()
        self._props = IBus.PropList()
        self._mode_prop = IBus.Property(key="mode", prop_type=IBus.PropType.NORMAL,
                                        label=_text("Mode"), tooltip=_text("Click to switch Bangla / English"),
                                        sensitive=True, visible=True)
        self._settings_prop = IBus.Property(key="settings", prop_type=IBus.PropType.NORMAL,
                                            label=_text("Popy Keyboard settings..."), sensitive=True, visible=True)
        self._props.append(self._mode_prop)
        self._props.append(self._settings_prop)
        try:
            self._update_mode_prop()
        except Exception:
            pass

    # --- helpers
    def _update_mode_prop(self):
        label = self.core.mode_label()
        self._mode_prop.set_symbol(_text(label))
        self._mode_prop.set_label(_text("%s  [%s]" % (label, self.core.layout_name())))
        self._mode_prop.set_icon("")
        self.update_property(self._mode_prop)

    def _reload_if_changed(self):
        m = config.mtime()
        if m != self._cfg_mtime:
            self._cfg_mtime = m
            self.core.apply_settings(config.load())
            self._update_mode_prop()

    def _show(self, a):
        if a.commit:
            self.commit_text(_text(a.commit))
        # key releases / ignored keys must not touch the preedit (that made the typed letters vanish)
        if not (a.consumed or a.commit or a.update):
            return
        if a.preedit:
            self.update_preedit_text(_text(a.preedit, True), len(a.preedit), True)
        else:
            self.hide_preedit_text()
        if a.aux:
            self.update_auxiliary_text(_text(a.aux), True)
        else:
            self.hide_auxiliary_text()
        if a.candidates:
            table = IBus.LookupTable.new(9, max(a.cursor, 0), a.cursor >= 0, True)
            for c in a.candidates:
                table.append_candidate(_text(c))
            self.update_lookup_table(table, True)
        else:
            self.hide_lookup_table()
        if a.mode_changed:
            self._update_mode_prop()

    # --- IBus callbacks
    def do_process_key_event(self, keyval, keycode, state):
        m = Mods(shift=bool(state & M.SHIFT_MASK), ctrl=bool(state & M.CONTROL_MASK),
                 alt=bool(state & M.MOD1_MASK), super=bool(state & M.SUPER_MASK),
                 caps=bool(state & M.LOCK_MASK), altgr=bool(state & M.MOD5_MASK),
                 release=bool(state & M.RELEASE_MASK))
        try:
            a = self.core.process(keyval, keycode, m)
            self._show(a)
            return a.consumed
        except Exception:  # never break the user's typing
            import traceback
            traceback.print_exc()
            return False

    def do_focus_in(self):
        self._reload_if_changed()
        self.register_properties(self._props)
        self._update_mode_prop()

    def do_focus_out(self):
        self._flush()

    def do_reset(self):
        self._flush()

    def do_enable(self):
        pass

    def do_disable(self):
        self._flush()

    def _flush(self):
        text = self.core.flush()
        if text:
            self.commit_text(_text(text))
        self.hide_preedit_text()
        self.hide_lookup_table()
        self.hide_auxiliary_text()

    def do_candidate_clicked(self, index, button, state):
        try:
            self._show(self.core.select_candidate(index))
        except Exception:
            import traceback
            traceback.print_exc()

    def do_property_activate(self, prop_name, state):
        if prop_name == "mode":
            self._show(self.core.toggle())
        elif prop_name == "settings":
            _launch_settings()

    def do_page_up(self):
        return False

    def do_page_down(self):
        return False


def _launch_settings():
    for exe in ("popy-keyboard-settings",):
        try:
            subprocess.Popen([exe])
            return
        except OSError:
            continue
    try:
        subprocess.Popen([sys.executable, "-m", "avrokb.gui.settings"])
    except OSError:
        pass


def all_engine_names():
    from . import layouts
    names = [config.ENGINE_PHONETIC, config.ENGINE_POPY, config.ENGINE_GENERIC]
    names += [config.FIXED_PREFIX + config.slug(l.name) for l in layouts.list_layouts(config.layout_dirs())]
    return names


class Factory(IBus.Factory):
    def __init__(self, bus):
        self._bus = bus
        self._n = 0
        super().__init__(connection=bus.get_connection(), object_path=IBus.PATH_FACTORY)
        for n in all_engine_names():
            self.add_engine(n, GObject.type_from_name("AvroKeyboardEngine"))

    def do_create_engine(self, engine_name):
        self._n += 1
        return AvroEngine(self._bus, "/org/freedesktop/IBus/Engine/%d" % self._n, engine_name)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    IBus.init()
    bus = IBus.Bus()
    loop = GLib.MainLoop()
    bus.connect("disconnected", lambda b: loop.quit())
    Factory(bus)
    if "--ibus" in argv:
        bus.request_name("org.freedesktop.IBus.PopyKeyboard", 0)
    else:
        comp = IBus.Component(name="org.freedesktop.IBus.PopyKeyboard", description="Popy Keyboard",
                              version=config.VERSION, license="MPL-2.0", author="OmicronLab / contributors",
                              homepage="https://www.omicronlab.com", textdomain="popy-keyboard")
        for n in all_engine_names():
            comp.add_engine(IBus.EngineDesc(name=n, longname="Popy Keyboard " + n, description="Bangla typing",
                                            language="bn", license="MPL-2.0", author="OmicronLab",
                                            icon="popy-keyboard", layout="us"))
        bus.register_component(comp)
    loop.run()


if __name__ == "__main__":
    main()
