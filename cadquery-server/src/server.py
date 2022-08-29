import os
import sys
import argparse
import traceback
import importlib

from flask import Flask, request


module = None
args = None
app = Flask(__name__)

def show(model):
    from jupyter_cadquery.utils import numpy_to_json
    from jupyter_cadquery.cad_objects import to_assembly
    from jupyter_cadquery.base import _tessellate_group

    return numpy_to_json(_tessellate_group(to_assembly(model)))

@app.route('/', methods = [ 'GET' ])
def root():
    global module

    module_name = request.args.get('mod', args.main)

    try:
        if module:
            print('Reloading module %s...' % module_name)
            importlib.reload(module)
        else:
            print('Importing module %s...' % module_name)
            module = importlib.import_module(module_name)

    except ModuleNotFoundError:
        return 'Can not import module "%s".' % module_name, 404

    except Exception as error:
        error_title = type(error).__name__
        stacktrace = traceback.format_exc()

        print(error_title + ': ' + str(error), '\n', stacktrace, file=sys.stderr)
        return '<h1>' + error_title + '</h1><p>' + str(error) + '</p><pre>' + stacktrace + '</pre>', 400

    try:
        model = getattr(module, args.render)
    except AttributeError:
        error = 'Variable "%s" is required to render the model.' % args.render

        print(error, file=sys.stderr)
        return error, 400

    return show(model)

def run(port: int):
    import cadquery

    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    global args

    parser = argparse.ArgumentParser(
            description='A web server that renders a 3d model of a CadQuery script loaded dynamically.')
    parser.add_argument('-p', '--port', type=int, default=5000,
        help='Server port (default: current 5000).')
    parser.add_argument('-d', '--dir', default='.',
        help='Path of the directory containing CadQuery scripts (default: current dir).')
    parser.add_argument('-m', '--main', default='main',
        help='Main module (default: main).')
    parser.add_argument('-r', '--render', default='result',
        help='Variable name of the model to render (default: result).')
    args = parser.parse_args()

    modules_path = os.path.abspath(os.path.join(os.getcwd(), args.dir))
    sys.path.insert(1, modules_path)

    run(args.port)


if __name__ == '__main__':
    main()
