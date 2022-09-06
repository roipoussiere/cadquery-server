'''Module cli: handles command line interface.'''

from sys import exit as sys_exit
import argparse
import os.path as op

from .server import run
from .module_manager import ModuleManager, ModuleManagerError
from .renderers import get_static_html
from . import __version__ as cqs_version


DEFAULT_PORT = 5000


def parse_args() -> argparse.Namespace:
    '''Parse cli arguments with argparse.'''

    parser = argparse.ArgumentParser(
        description='A web server that renders a 3d model of a CadQuery script loaded dynamically.')

    parser.add_argument('-V', '--version', action='store_true',
        help='Print CadQuery Server version and exit.')

    parser.add_argument('target', nargs='?', default='.',
        help='Python file or folder containing CadQuery script to load (default: ".").')

    parser.add_argument('-l', '--list', action='store_true',
        help='List available modules for the current target and exit.')
    parser.add_argument('-e', '--export', action='store', default='', nargs='?', metavar='FILE',
        help='Export a static html file that work without server (default: "<module_name>.html").')
    parser.add_argument('-m', '--minify', action='store_true',
        help='Minify output when exporting to html.')

    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
        help=f'Server port (default: { DEFAULT_PORT }).')
    parser.add_argument('-d', '--dead', action='store_true',
        help='Disable live reloading.')

    parser.add_argument('--ui-hide', metavar='LIST',
        help='ui: a comma-separated list of buttons to hide'
            + ', among: axes, axes0, grid, ortho, more, help, all.')
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


def get_ui_options(args: argparse.Namespace) -> dict:
    '''Generate the options dictionnary used in three-cad-viewer, based on cli options.'''

    hidden_buttons = []
    if args.ui_hide:
        hidden_buttons = args.ui_hide.split(',')
        if 'all' in hidden_buttons:
            hidden_buttons = [ 'axes', 'axes0', 'grid', 'ortho', 'more', 'help' ]

    return {
        'hideButtons': hidden_buttons,
        'glass': args.ui_glass,
        'theme': args.ui_theme,
        'control': 'trackball' if args.ui_trackball else 'orbit',
        'ortho': not args.ui_perspective,
        'grid': [ 'x' in args.ui_grid, 'y' in args.ui_grid, 'z' in args.ui_grid ] \
            if args.ui_grid else [ False, False, False ],
        'transparent': args.ui_transparent,
        'blackEdges': args.ui_black_edges
    }


def main() -> None:
    '''Main function, called when using the `cq-server` command.'''

    args = parse_args()

    try:
        module_manager = ModuleManager(args.target)
    except ModuleManagerError as err:
        sys_exit(err)

    ui_options = get_ui_options(args)

    if args.version:
        print(f'CadQuery Server version: { cqs_version }')
        sys_exit()

    if args.list:
        module_manager.update_ignore_list()
        print('\n'.join(module_manager.get_modules_name()))
        sys_exit()

    if args.export == '':
        run(args.port, module_manager, ui_options, args.dead)
    else:

        if module_manager.target_is_dir:
            sys_exit('Exporting a folder to html is not yet possible.')

        static_html = get_static_html(module_manager, ui_options, args.minify)
        file_name = args.export if args.export else f'{ op.splitext(args.target)[0] }.html'

        with open(file_name, 'w', encoding='utf-8') as html_file:
            html_file.write(static_html)
        print(f'File exported in { file_name }.')


if __name__ == '__main__':
    main()
