import os
import sys
import argparse
import traceback

from flask import Flask


DEFAULT_MODULE_NAME = 'main'
MODEL_VARIABLE_NAME = 'result'

app = Flask(__name__)


def show(model):
    from jupyter_cadquery.utils import numpy_to_json
    from jupyter_cadquery.cad_objects import to_assembly
    from jupyter_cadquery.base import _tessellate_group

    return numpy_to_json(_tessellate_group(to_assembly(model)))


@app.route('/<module_name>', methods = [ 'GET' ])
def root(module_name=DEFAULT_MODULE_NAME):
    try:
        module = __import__(module_name)

    except ModuleNotFoundError:
        return 'Can not import module "%s".' % module_name, 404

    except Exception as error:
        error_title = type(error).__name__
        stacktrace = traceback.format_exc()

        print(error_title + ': ' + str(error), '\n', stacktrace, file=sys.stderr)
        return '<h1>' + error_title + '</h1><p>' + str(error) + '</p><pre>' + stacktrace + '</pre>', 400

    try:
        model = getattr(module, MODEL_VARIABLE_NAME)
    except AttributeError:
        error = 'Variable "%s" is required to render the model.' % MODEL_VARIABLE_NAME

        print(error, file=sys.stderr)
        return error, 400

    return show(model)

def run(port: int):
    import cadquery

    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    parser = argparse.ArgumentParser(description='A web server that renders a 3d model of a CadQuery script loaded dynamically.')
    parser.add_argument('dir', help='Path of the directory containing CadQuery scripts')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Server port')
    args = parser.parse_args()

    modules_path = os.path.abspath(os.path.join(os.getcwd(), args.dir))
    sys.path.insert(1, modules_path)

    run(args.port)


if __name__ == '__main__':
    main()
