import cadquery as cq
from jupyter_cadquery.utils import numpy_to_json
from jupyter_cadquery.cad_objects import to_assembly
from jupyter_cadquery.base import _tessellate_group

from flask import Flask, request


app = Flask(__name__)
json_result = '[{}, {}]'


def show(model):
    global json_result
    json_result = numpy_to_json(_tessellate_group(to_assembly(model)))


@app.route('/', methods = [ 'GET', 'POST' ])
def hello_world():
    if request.method == 'GET':
        return 'Please send a CadQuery Python script in a POST request.\n'
    elif request.method == 'POST':
        # exec(compile(request.get_data().decode(), '-', 'exec'))
        exec(request.get_data().decode())
        return json_result


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
