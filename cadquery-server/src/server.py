import os
import sys
import argparse

from flask import Flask


DEFAULT_MODULE_NAME = 'main'

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

    model = getattr(module, 'result')
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
