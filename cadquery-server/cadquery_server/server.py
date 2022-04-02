import cadquery
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
def root():
    if request.method == 'GET':
        return 'Please send a CadQuery Python script in a POST request.\n'
    elif request.method == 'POST':
        exec(request.get_data().decode())
        return json_result


def run():
    app.run(host='0.0.0.0', debug=False)
