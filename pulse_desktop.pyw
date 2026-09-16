from __future__ import annotations

import argparse

from pulse.app import PulseApp


def parse_args(argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--pid', type=int)
    return parser.parse_known_args(argv)[0]


def main(argv=None):
    args = parse_args(argv)
    app = PulseApp()
    if args.pid:
        app.filter_var.set(str(args.pid))
        attempts = {'left': 40}

        def focus_pid():
            iid = str(args.pid)
            if app.tree.exists(iid):
                app.tree.selection_set(iid)
                app.tree.see(iid)
                app._select()
                return
            attempts['left'] -= 1
            if attempts['left'] > 0:
                app.after(250, focus_pid)

        app.after(250, focus_pid)
    app.mainloop()


if __name__ == '__main__':
    main()
