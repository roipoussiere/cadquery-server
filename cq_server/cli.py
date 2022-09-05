from sys import exit as sys_exit
import argparse
import os.path as op

from .server import run, get_static_html
from .module_manager import ModuleManager, ModuleManagerError
from . import __version__ as cqs_version


DEFAULT_PORT = 5000


def parse_args():
    parser = argparse.ArgumentParser(
            description='A web server that renders a 3d model of a CadQuery script loaded dynamically.')

    parser.add_argument('-V', '--version', action='store_true',
        help='Print CadQuery Server version and exit.')

    parser.add_argument('target', nargs='?', default='.',
        help='Python file or folder containing CadQuery script to load (default: ".").')

    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
        help='Server port (default: %d).' % DEFAULT_PORT)
    parser.add_argument('-e', '--export', action='store', default='', nargs='?', metavar='FILE',
        help='Export a static html file that work without the server (default: "<module_name>.html").')
    parser.add_argument('-b', '--blind', action='store_true',
        help='Disable file watcher.')

    parser.add_argument('--ui-hide', metavar='LIST',
        help='ui: a comma-separated list of buttons to hide, among: axes, axes0, grid, ortho, more, help.')
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

    try:
        module_manager = ModuleManager(args.target)
    except ModuleManagerError as err:
        sys_exit(err)

    ui_options = get_ui_options(args)

    if args.version:
        print('CadQuery Server version: %s' % cqs_version)
        sys_exit()

    if args.export == '':
        run(args.port, module_manager, ui_options, args.blind)
    else:

        if module_manager.target_is_dir:
            sys_exit('Exporting a folder to html is not yet possible.')

        static_html = get_static_html(module_manager, ui_options)
        file_name = args.export if args.export else '%s.html' % op.splitext(args.target)[0]

        with open(file_name, 'w') as html_file:
            html_file.write(static_html)
        print('File exported in %s.' % file_name)


if __name__ == '__main__':
    main()
