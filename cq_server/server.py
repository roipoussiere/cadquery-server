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

WATCH_PERIOD = 0.3

app = Flask(__name__, static_url_path='/static')


def get_static_html(module_manager, ui_options, minify=True):
    viewer_css_path = op.join(STATIC_DIR, 'viewer.css')
    viewer_js_path = op.join(STATIC_DIR, 'viewer.js')
    template_path = op.join(TEMPLATES_DIR, 'viewer.html')

    with open(viewer_css_path) as css_file:
        viewer_css = '\n' + css_file.read() + '\n'

    with open(viewer_js_path) as js_file:
        viewer_js = '\n' + js_file.read() + '\n'

    with open(template_path) as template_file:
        template = Template(template_file.read())

    module_manager.init()

    html = template.render(
        static=True,
        viewer_css=viewer_css,
        viewer_js=viewer_js,
        options=ui_options,
        modules_name=module_manager.get_modules_name(),
        data=module_manager.get_data()
    )

    if minify:
        import minify_html

        html = minify_html.minify(
            html,
            minify_js=True,
            minify_css=True,
            remove_processing_instructions=True
        )

    return html

def run(port, module_manager, ui_options, is_blind=False):

    @app.route('/', methods = [ 'GET' ])
    def _root():
        if module_manager.target_is_dir:
            module_manager.module_name = request.args.get('m')

        return render_template(
            'viewer.html',
            options=ui_options,
            modules_name=module_manager.get_modules_name(),
            data=module_manager.get_data()
        )

    @app.route('/html', methods = [ 'GET' ])
    def _html():
        if module_manager.target_is_dir:
            module_manager.module_name = request.args.get('m')

        return get_static_html(module_manager, ui_options)

    @app.route('/json', methods = [ 'GET' ])
    def _json():
        if module_manager.target_is_dir:
            module_manager.module_name = request.args.get('m')

        try:
            model = module_manager.get_model()
        except ModuleManagerError as error:
            return {
                'error': error.message,
                'stacktrace': error.stacktrace
            }, 400

        return {
            'module_name': module_manager.module_name,
            'model': model
        }

    @app.route('/events', methods = [ 'GET' ])
    def _events():
        def stream():
            while True:
                yield events_queue.get()

        return Response(stream(), mimetype='text/event-stream')

    def watchdog():
        SSE_MESSAGE_TEMPLATE = 'event: file_update\ndata: %s\n\n'

        while(True):
            last_updated_file = module_manager.get_last_updated_file()
    
            if last_updated_file:
                module_manager.module_name = op.basename(last_updated_file)[:-3]
                data = {
                    'module_name': module_manager.module_name,
                    'model': module_manager.get_model()
                }
                events_queue.put(SSE_MESSAGE_TEMPLATE % json.dumps(data))
            sleep(WATCH_PERIOD)

    events_queue = Queue(maxsize = 3)
    module_manager.init()
    if not is_blind:
        watchdog_thread = Thread(target=watchdog, daemon=True)
        watchdog_thread.start()
    app.run(host='0.0.0.0', port=port, debug=False)
