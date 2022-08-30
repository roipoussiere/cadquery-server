import os
import sys
import argparse
import traceback
import importlib

from flask import Flask, request


DEFAULT_PORT = 5000
DEFAULT_DIR = '.'
DEFAULT_MAIN = 'main'
DEFAULT_MODEL_VAR = 'result'


class CadQueryModuleManagerError(Exception):
    def __init__(self, message, stacktrace=''):
        self.message = message
        self.stacktrace = stacktrace

        print(message, file=sys.stderr)
        if stacktrace:
            print(stacktrace, file=sys.stderr)

        super().__init__(self.message)


class CadQueryModuleManager:
    def __init__(self, dir=DEFAULT_DIR, main=DEFAULT_MAIN, model_var=DEFAULT_MODEL_VAR):
        self.dir = dir
        self.main = main
        self.model_var = model_var

        self.module = None

    def init(self):
        print('Importing CadQuery...', end=' ', flush=True)
        import cadquery
        print('done.')

        modules_path = os.path.abspath(os.path.join(os.getcwd(), self.dir))
        sys.path.insert(1, modules_path)

    def render_module(self, module_name):
        self.load_module(module_name)
        model = self.get_model()
        return self.render_model(model)

    def render_model(self, model):
        from jupyter_cadquery.utils import numpy_to_json
        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group

        return numpy_to_json(_tessellate_group(to_assembly(model)))

    def load_module(self, module_name):
        if not module_name:
            module_name = self.main

        try:
            if self.module:
                print('Reloading module %s...' % module_name)
                importlib.reload(self.module)
            else:
                print('Importing module %s...' % module_name)
                self.module = importlib.import_module(module_name)

        except ModuleNotFoundError:
            raise CadQueryModuleManagerError('Can not import module "%s".' % module_name)

        except Exception as error:
            raise CadQueryModuleManagerError(type(error).__name__ + ': ' + str(error), traceback.format_exc())

    def get_model(self):
        try:
            return getattr(self.module, self.model_var)
        except AttributeError:
            raise CadQueryModuleManagerError('Variable "%s" is required to render the model.' % self.model_var)


def parse_args():
    parser = argparse.ArgumentParser(
            description='A web server that renders a 3d model of a CadQuery script loaded dynamically.')

    parser.add_argument('-p', '--port', type=int, default=5000,
        help='Server port (default: 5000).')
    parser.add_argument('-d', '--dir', default='.',
        help='Path of the directory containing CadQuery scripts (default: current dir).')
    parser.add_argument('-m', '--main', default='main',
        help='Main module (default: main).')
    parser.add_argument('-r', '--render', default='result',
        help='Variable name of the model to render (default: result).')

    return parser.parse_args()


app = Flask(__name__)

def run_cadquery_server(port, dir, main, render):
    cqmm = CadQueryModuleManager(dir, main, render)
    cqmm.init()

    @app.route('/', methods = [ 'GET' ])
    def root():
        try:
            return cqmm.render_module(request.args.get('mod'))
        except CadQueryModuleManagerError as err:
            response = '<p>%s</p>' % err.message
            if err.stacktrace:
                response += '<pre>%s</pre>' % err.stacktrace
            return response, 400

    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    args = parse_args()
    run_cadquery_server(args.port, args.dir, args.main, args.render)


if __name__ == '__main__':
    main()
