from flask import Flask, request

from .module_manager import CadQueryModuleManagerError


app = Flask(__name__)

def run(port, module_manager):
    module_manager.init()

    @app.route('/', methods = [ 'GET' ])
    def root():
        module_name = request.args.get('module')
        output = request.args.get('output')

        try:
            return module_manager.render(module_name, output)
        except CadQueryModuleManagerError as err:
            response = '<p>%s</p>' % err.message
            if err.stacktrace:
                response += '<pre>%s</pre>' % err.stacktrace
            return response, 400

    app.run(host='0.0.0.0', port=port, debug=False)
