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

    parser.add_argument('--ui-hide', metavar='LIST',
        help='ui: a comma-separated list of buttons to disable, among: axes, axes0, grid, ortho, more, help.')
    parser.add_argument('--ui-glass', action='store_true',
        help='ui: activate tree view glass mode.')
    parser.add_argument('--ui-theme', choices=['light', 'dark'], metavar='THEME',
        help='ui: set ui theme, light or dark (default: browser config).')
    parser.add_argument('--ui-trackball', action='store_true',
        help='ui: set control mode to trackball instead orbit.')
    parser.add_argument('--ui-perspective', action='store_true',
        help='ui: set camera view to perspective instead orthogonal.')
    parser.add_argument('--ui-grid', metavar='AXES',
        help='ui: display a grid in specified axes (x, y, z, xy, etc.).')
    parser.add_argument('--ui-transparent', action='store_true',
        help='ui: make objects semi-transparent.')
    parser.add_argument('--ui-black-edges', action='store_true',
        help='ui: make edges black.')

    return parser.parse_args()


def get_ui_options(args):
    return {
        'hideButtons': args.ui_hide.split(',') if args.ui_hide else [],
        'glass': args.ui_glass,
        'theme': args.ui_theme,
        'control': 'trackball' if args.ui_trackball else 'orbit',
        'ortho': not args.ui_perspective,
        'grid': [ 'x' in args.ui_grid, 'y' in args.ui_grid, 'z' in args.ui_grid ] if args.ui_grid else [ False, False, False ],
        'transparent': args.ui_transparent,
        'blackEdges': args.ui_black_edges
    }


def main():
    args = parse_args()
    module_manager = CadQueryModuleManager(args.dir, args.module)
    run(args.port, module_manager, get_ui_options(args))


if __name__ == '__main__':
    main()
