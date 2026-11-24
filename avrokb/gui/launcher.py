"""Command line entry: popy-keyboard [tray|settings|viewer|convert|spell|about]"""
import sys


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    sub = argv[0] if argv else "tray"
    rest = argv[1:]
    if sub == "settings":
        from . import settings as m; m.main()
    elif sub == "viewer":
        from . import viewer as m; m.main(rest)
    elif sub == "convert":
        from . import converter as m; m.main()
    elif sub == "spell":
        from . import spellgui as m; m.main()
    elif sub == "about":
        from .common import show_about; show_about()
    elif sub == "tray":
        from . import tray as m; m.main()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
