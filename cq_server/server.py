import json
from threading import Thread
from queue import Queue
from time import sleep

from flask import Flask, request, render_template, Response

from .module_manager import CadQueryModuleManagerError


WATCH_PERIOD = 0.1

app = Flask(__name__, static_url_path='/static')


def run(port, module_manager, ui_options):

    @app.route('/', methods = [ 'GET' ])
    def _root():
        return render_template(
            'viewer.html',
            module=request.args.get('module', module_manager.default_module_name),
            options=ui_options
        )

    @app.route('/json', methods = [ 'GET' ])
    def _json():
        module_manager.module_name = request.args.get('module')

        try:
            return {
                'model': module_manager.get_model()
            }
        except CadQueryModuleManagerError as err:
            return {
                'error': err.message,
                'stacktrace': err.stacktrace
            }, 400

    @app.route('/events', methods = [ 'GET' ])
    def _events():
        def stream():
            while True:
                yield events_queue.get()

        return Response(stream(), mimetype='text/event-stream')

    def watch_file():
        SSE_MESSAGE_TEMPLATE = 'event: file_update\ndata: %s\n\n'
        while(True):
            if module_manager.is_file_updated():
                data = {
                    'model': module_manager.get_model()
                }
                events_queue.put(SSE_MESSAGE_TEMPLATE % json.dumps(data))
            sleep(WATCH_PERIOD)

    events_queue = Queue(maxsize = 3)
    module_manager.init()
    watchdog = Thread(target=watch_file, daemon=True)
    watchdog.start()
    app.run(host='0.0.0.0', port=port, debug=False)
