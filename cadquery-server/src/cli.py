import argparse

from .server import run
from .module_manager import CadQueryModuleManager


DEFAULT_PORT = 5000
DEFAULT_DIR = '.'
DEFAULT_MODULE = 'main'
DEFAULT_MODEL_VAR = 'result'
DEFAULT_OUTPUT_FORMAT = 'json'


def parse_args():
    parser = argparse.ArgumentParser(
            description='A web server that renders a 3d model of a CadQuery script loaded dynamically.')

    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
        help='Server port (default: %d).' % DEFAULT_PORT)
    parser.add_argument('-d', '--dir', default=DEFAULT_DIR,
        help='Path of the directory containing CadQuery scripts (default: `%s`).' % DEFAULT_DIR)
    parser.add_argument('-m', '--main', default=DEFAULT_MODULE,
        help='Default module (default: %s).' % DEFAULT_MODULE)
    parser.add_argument('-r', '--render', default=DEFAULT_MODEL_VAR,
        help='Variable name of the model to render (default: %s).' % DEFAULT_MODEL_VAR)
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT_FORMAT,
        help='Default output format (default: %s).' % DEFAULT_OUTPUT_FORMAT)

    return parser.parse_args()


def main():
    args = parse_args()
    module_manager = CadQueryModuleManager(args.dir, args.main, args.render, args.output)
    run(args.port, module_manager)


if __name__ == '__main__':
    main()
