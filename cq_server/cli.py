import argparse

from .server import run
from .module_manager import CadQueryModuleManager


DEFAULT_PORT = 5000
DEFAULT_DIR = '.'
DEFAULT_MODULE = 'main'


def parse_args():
    parser = argparse.ArgumentParser(
            description='A web server that renders a 3d model of a CadQuery script loaded dynamically.')

    parser.add_argument('dir', nargs='?', default=DEFAULT_DIR,
        help='Path of the directory containing CadQuery scripts (default: "%s").' % DEFAULT_DIR)
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
        help='Server port (default: %d).' % DEFAULT_PORT)
    parser.add_argument('-m', '--module', default=DEFAULT_MODULE, metavar='MOD',
        help='Default Python module to load (default: "%s").' % DEFAULT_MODULE)

    parser.add_argument('--ui-glass', action='store_true',
        help='ui: activate glass mode.')
    parser.add_argument('--ui-hide', metavar='LIST',
        help='ui: disable a list of buttons, separated by commas.')

    return parser.parse_args()


def get_ui_options(args):
    return {
        'hideButtons': args.ui_hide.split(',') if args.ui_hide else [],
        'glass': args.ui_glass
    }


def main():
    args = parse_args()
    module_manager = CadQueryModuleManager(args.dir, args.module)
    run(args.port, module_manager, get_ui_options(args))


if __name__ == '__main__':
    main()
