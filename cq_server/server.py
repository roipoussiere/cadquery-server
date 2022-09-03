import json
from threading import Thread
from queue import Queue
from time import sleep
import os.path as op

from flask import Flask, request, render_template, Response
from jinja2 import Template

from .module_manager import ModuleManagerError


APP_DIR = op.dirname(__file__)
STATIC_DIR = op.join(APP_DIR, 'static')
TEMPLATES_DIR = op.join(APP_DIR, 'templates')

WATCH_PERIOD = 0.1

app = Flask(__name__, static_url_path='/static')

def get_static_html(module_manager, ui_options):
    if module_manager.main_module_name == '__index__':
        raise NameError('Target must be a file when exporting to html')

    viewer_css_path = op.join(STATIC_DIR, 'viewer.css')
    viewer_js_path = op.join(STATIC_DIR, 'viewer.js')
    template_path = op.join(TEMPLATES_DIR, 'viewer_static.html')

    with open(viewer_css_path) as css_file:
        viewer_css = '\n' + css_file.read() + '\n'

    with open(viewer_js_path) as js_file:
        viewer_js = '\n' + js_file.read() + '\n'

    with open(template_path) as template_file:
        template = Template(template_file.read())

    module_manager.init()

    return template.render(
        viewer_css=viewer_css,
        viewer_js=viewer_js,
        module=module_manager.module_name,
        options=ui_options,
        data={
            'model': module_manager.get_model()
        }
    )

def run(port, module_manager, ui_options):

    @app.route('/', methods = [ 'GET' ])
    def _root():
        module_manager.set_module_name(request.args.get('m'))

        if module_manager.module_name == '__index__':
            return render_template(
                'index.html',
                modules_name=module_manager.get_available_modules()
            )
        else:
            return render_template(
                'viewer.html',
                module_name=module_manager.module_name,
                options=ui_options
            )

    @app.route('/html', methods = [ 'GET' ])
    def _html():
        module_manager.set_module_name(request.args.get('m'))

        try:
            return get_static_html(module_manager, ui_options)
        except NameError as error:
            return error, 400

    @app.route('/json', methods = [ 'GET' ])
    def _json():
        module_manager.set_module_name(request.args.get('m'))

        try:
            model = module_manager.get_model()
        except ModuleManagerError as error:
            return {
                'error': error.message,
                'stacktrace': error.stacktrace
            }, 400

        return {
            'model': model
        }

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