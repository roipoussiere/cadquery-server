from flask import Flask, request

from .module_manager import CadQueryModuleManagerError


app = Flask(__name__)

def run(port, module_manager):
    module_manager.init()

    @app.route('/', methods = [ 'GET' ])
    def root():
        try:
            return module_manager.render_module(request.args.get('mod'))
        except CadQueryModuleManagerError as err:
            response = '<p>%s</p>' % err.message
            if err.stacktrace:
                response += '<pre>%s</pre>' % err.stacktrace
            return response, 400

    app.run(host='0.0.0.0', port=port, debug=False)
