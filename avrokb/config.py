"""Settings + data directory discovery (system install, user dir, or source tree)."""
import json
import os
import re

APP = "popy-keyboard"
VERSION = "ExtremeMOD"

DEFAULTS = {
    "layout": "Avro Phonetic",       # 'Avro Phonetic', 'Popy', or the name of a .avrolayout
    "toggle_key": "Ctrl+Space",      # Ctrl+Space, Shift+Space, Right Win, Right Ctrl, F12
    "show_preview": True,            # candidate / preview window under the cursor
    "start_mode": "bangla",          # bangla | english
    "output_ansi": False,            # ANSI (Bijoy) output instead of Unicode
    "avro_autocorrect": True,
    "avro_suggestions": True,
    "popy_autocorrect": True,        # Popy: match words with the dictionary (+ suggestions in the preview)
    "popy_greedy": True,             # Popy greedy mode: listed conjuncts join by themselves (off = Shift for every conjunct)
    "jo_nukta": False,
    "vowel_formatting": True,
    "old_style_reph": True,
    "fix_chandra": True,
}
TOGGLE_KEYS = ["Ctrl+Space", "Shift+Space", "Right Win", "Right Ctrl", "F12"]
BUILTIN_LAYOUTS = ["Avro Phonetic", "Popy"]


OLD_APP = "avro-keyboard"               # name before the rename to Popy Keyboard


def _base(var, default):
    return os.environ.get(var) or os.path.expanduser(default)


def _migrated(base):
    """New dir; if only the old Avro-named one exists, keep using it so settings and layouts are not lost."""
    new, old = os.path.join(base, APP), os.path.join(base, OLD_APP)
    return old if (not os.path.isdir(new) and os.path.isdir(old)) else new


def config_dir():
    return _migrated(_base("XDG_CONFIG_HOME", "~/.config"))


def user_data_dir():
    return _migrated(_base("XDG_DATA_HOME", "~/.local/share"))


def settings_path():
    return os.path.join(config_dir(), "settings.json")


def package_data_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def layout_dirs():
    """Search order: user dir first (so users can add/override layouts), then bundled."""
    dirs = [os.path.join(user_data_dir(), "layouts")]
    for base in ("/usr/share/%s" % APP, package_data_dir()):
        d = os.path.join(base, "layouts")
        if d not in dirs:
            dirs.append(d)
    return dirs


def load():
    s = dict(DEFAULTS)
    try:
        with open(settings_path(), encoding="utf-8") as f:
            s.update({k: v for k, v in json.load(f).items() if k in DEFAULTS})
    except (OSError, ValueError):
        pass
    return s


def save(s):
    os.makedirs(config_dir(), exist_ok=True)
    tmp = settings_path() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({k: s.get(k, v) for k, v in DEFAULTS.items()}, f, ensure_ascii=False, indent=2)
    os.replace(tmp, settings_path())


def mtime():
    try:
        return os.path.getmtime(settings_path())
    except OSError:
        return 0.0


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


ENGINE_PHONETIC = "popy-phonetic"
ENGINE_POPY = "popy-layout"
ENGINE_GENERIC = "popy-keyboard"        # layout chosen in the settings window
FIXED_PREFIX = "popy-fixed-"


def engine_layout(engine_name, settings, layout_names):
    """Layout used by an IBus engine name; layout_names = names of the installed fixed layouts."""
    engine_name = engine_name.replace("avro-fixed-", FIXED_PREFIX, 1) if engine_name.startswith("avro-fixed-") else \
        {"avro-phonetic": ENGINE_PHONETIC, "avro-popy": ENGINE_POPY, "avro-keyboard": ENGINE_GENERIC}.get(engine_name, engine_name)
    if engine_name == ENGINE_PHONETIC:
        return "Avro Phonetic"
    if engine_name == ENGINE_POPY:
        return "Popy"
    if engine_name.startswith(FIXED_PREFIX):
        for n in layout_names:
            if FIXED_PREFIX + slug(n) == engine_name:
                return n
    return settings.get("layout", "Avro Phonetic")
