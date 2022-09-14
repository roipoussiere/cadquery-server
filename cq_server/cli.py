'''Module cli: handles command line interface.'''

from sys import exit as sys_exit
import argparse
import os.path as op

from .server import run
from .module_manager import ModuleManager, ModuleManagerError
from .renderers import to_html, to_json
from . import __version__ as cqs_version


DEFAULT_PORT = 5000


def parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    '''Parse cli arguments with argparse.'''

    parser.description = 'A web server that renders a 3d model of a CadQuery script loaded dynamically.'
    parser.add_argument('-V', '--version', action='store_true',
        help='print CadQuery Server version and exit')

    subparsers = parser.add_subparsers(title='subcommands', dest='cmd',
        description='type <command> -h for subcommand usage')

    parser_run = subparsers.add_parser('run', help='run the server')
    parser_run.add_argument('target', nargs='?', default='.',
        help='python file or folder containing CadQuery script to load (default: ".")')
    parser_run.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
        help=f'server port (default: { DEFAULT_PORT })')
    parser_run.add_argument('-r', '--raise', dest='should_raise', action='store_true',
        help=f'when an error happen, raise it instead showing its title')
    parser_run.add_argument('-d', '--dead', action='store_true',
        help='disable live reloading')
    add_ui_options(parser_run)

    parser_build = subparsers.add_parser('build', help='build static website')
    parser_build.add_argument('target', nargs='?', default='.',
        help='python file or folder containing CadQuery script to load (default: ".")')
    parser_build.add_argument('destination', nargs='?',
        help='output file path (default: "<module_name>.html"), or `-` for stdout.')
    parser_build.add_argument('-f', '--format', choices=[ 'html', 'json' ], metavar='FMT',
        help='output format: html or json (default: file extension, or html if not given)')
    parser_build.add_argument('-m', '--minify', action='store_true',
        help='minify output when exporting to html')
    add_ui_options(parser_build)

    parser_list = subparsers.add_parser('info',
        help='show information about the current target and exit')
    parser_list.add_argument('target', nargs='?', default='.',
        help='python file or folder containing CadQuery script to load (default: ".")')

    return parser.parse_args()


def add_ui_options(parser: argparse.ArgumentParser):
    parse_ui = parser.add_argument_group('user interface options')
    parse_ui.add_argument('--ui-hide', metavar='LIST',
        help='a comma-separated list of buttons to hide'
            + ', among: axes, axes0, grid, ortho, more, help, all')
    parse_ui.add_argument('--ui-glass', action='store_true',
        help='activate tree view glass mode')
    parse_ui.add_argument('--ui-theme', choices=['light', 'dark'], metavar='THEME',
        help='set ui theme: light or dark (default: browser config)')
    parse_ui.add_argument('--ui-trackball', action='store_true',
        help='set control mode to trackball instead orbit')
    parse_ui.add_argument('--ui-perspective', action='store_true',
        help='set camera view to perspective instead orthogonal')
    parse_ui.add_argument('--ui-grid', metavar='AXES',
        help='display a grid in specified axes (x, y, z, xy, etc.)')
    parse_ui.add_argument('--ui-transparent', action='store_true',
        help='make objects semi-transparent')
    parse_ui.add_argument('--ui-black-edges', action='store_true',
        help='make edges black')

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

    parser = argparse.ArgumentParser()
    args = parse_args(parser)

    if args.version:
        print(f'CadQuery Server version: { cqs_version }')
        sys_exit()

    if not args.cmd or args.cmd not in [ 'run', 'build', 'info' ]:
        parser.print_help()
        sys_exit()

    should_raise = (args.cmd == 'run' and args.should_raise)
    try:
        module_manager = ModuleManager(args.target, should_raise)
    except ModuleManagerError as err:
        sys_exit(err)

    if args.cmd == 'info':
        module_manager.update_ignore_list()
        print('Ignored modules: ' + '\n'.join(module_manager.get_modules_name()))
        sys_exit()

    ui_options = get_ui_options(args)

    if args.cmd == 'run':
        run(args.port, module_manager, ui_options, args.dead)

    if args.cmd == 'build':
        if module_manager.target_is_dir:
            sys_exit('Exporting a folder to html is not yet possible.')

        file_ext = op.splitext(args.destination)[1] if args.destination else None
        if file_ext == '.html' or (not file_ext and not args.format):
            args.format = 'html'
        elif file_ext == '.json':
            args.format = 'json'

        if args.format == 'html':
            output_content = to_html(module_manager, ui_options, args.minify)
        elif args.format == 'json':
            output_content = to_json(module_manager)
        else:
            sys_exit('Output format not recognized.')

        if not args.destination:
             args.destination = f'{ op.splitext(args.target)[0] }.{ args.format }'

        if args.destination == '-':
            print(output_content)
        else:
            with open(args.destination, 'w', encoding='utf-8') as html_file:
                html_file.write(output_content)
            print(f'File exported in { args.destination }.')


if __name__ == '__main__':
    main()
