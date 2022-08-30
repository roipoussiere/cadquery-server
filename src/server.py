from flask import Flask, request, render_template

from .module_manager import CadQueryModuleManagerError


app = Flask(__name__)


def run(port, module_manager):
    module_manager.init()

    @app.route('/', methods = [ 'GET' ])
    def root():
        return render_template(
            'viewer.html',
            module=request.args.get('module'),
            object=request.args.get('object')
        )

    @app.route('/json', methods = [ 'GET' ])
    def json():
        module_name = request.args.get('module')
        object_var_name = request.args.get('object')

        try:
            return module_manager.render(module_name, object_var_name, 'json')
        except CadQueryModuleManagerError as err:
            response = {
                'msg': err.message,
                'stacktrace': err.stacktrace
            }
            return response, 400

    app.run(host='0.0.0.0', port=port, debug=False)
