import argparse

import cadquery
from flask import Flask, request


app = Flask(__name__)
json_result = '[{}, {}]'


def show(model):
    from jupyter_cadquery.utils import numpy_to_json
    from jupyter_cadquery.cad_objects import to_assembly
    from jupyter_cadquery.base import _tessellate_group

    global json_result
    json_result = numpy_to_json(_tessellate_group(to_assembly(model)))


@app.route('/', methods = [ 'GET', 'POST' ])
def root():
    if request.method == 'GET':
        return 'Please send a CadQuery Python script in a POST request.\n'
    elif request.method == 'POST':
        exec(request.get_data().decode(), globals())
        return json_result


def run(port: int):
    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    parser = argparse.ArgumentParser(description='A web server that executes a given CadQuery code and returns the generated model as a threejs object.')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Server port')
    args = parser.parse_args()

    run(args.port)


if __name__ == '__main__':
    main()
