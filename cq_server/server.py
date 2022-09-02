import json
from threading import Thread
from queue import Queue
from time import sleep
import os.path as op

from flask import Flask, request, render_template, Response

from .module_manager import CadQueryModuleManagerError


STATIC_DIR = op.join(op.dirname(__file__), 'static')
WATCH_PERIOD = 0.1

app = Flask(__name__, static_url_path='/static')


def run(port, module_manager, ui_options):

    def update_module_name():
        module_manager.module_name = request.args.get('module', module_manager.default_module_name)

    @app.route('/', methods = [ 'GET' ])
    def _root():
        update_module_name()

        return render_template(
            'viewer.html',
            module=module_manager.module_name,
            options=ui_options
        )

    @app.route('/html', methods = [ 'GET' ])
    def _html():
        update_module_name()

        viewer_css_path = op.join(STATIC_DIR, 'viewer.css')
        viewer_js_path = op.join(STATIC_DIR, 'viewer.js')

        with open(viewer_css_path) as css_file:
            viewer_css = '\n' + css_file.read() + '\n'

        with open(viewer_js_path) as js_file:
            viewer_js = '\n' + js_file.read() + '\n'

        return render_template(
            'viewer_static.html',
            viewer_css=viewer_css,
            viewer_js=viewer_js,
            module=module_manager.module_name,
            options=ui_options,
            data={
                'model': module_manager.get_model()
            }
        )

    @app.route('/json', methods = [ 'GET' ])
    def _json():
        update_module_name()

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
