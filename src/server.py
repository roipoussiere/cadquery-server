import threading
import time

from flask import Flask, request, render_template, Response

from .module_manager import CadQueryModuleManagerError


WATCH_PERIOD = 0.5

app = Flask(__name__, static_url_path='/static')


def run(port, module_manager):

    @app.route('/', methods = [ 'GET' ])
    def root():
        return render_template(
            'viewer.html',
            module=request.args.get('module', module_manager.default_module_name),
            object=request.args.get('object', module_manager.default_object_var)
        )

    @app.route('/json', methods = [ 'GET' ])
    def json():
        module_manager.module_name = request.args.get('module')
        module_manager.object_var = request.args.get('object')

        try:
            return module_manager.render_json()
        except CadQueryModuleManagerError as err:
            response = {
                'msg': err.message,
                'stacktrace': err.stacktrace
            }
            return response, 400

    def watch_file():
        while(True):
            is_updated = module_manager.is_file_updated()
            time.sleep(WATCH_PERIOD)

    module_manager.init()
    watchdog = threading.Thread(target=watch_file, daemon=True)
    watchdog.start()
    app.run(host='0.0.0.0', port=port, debug=False)
