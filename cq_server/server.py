'''Module server: used to run the Flask web server and render Jinja templates.'''

import json
from threading import Thread
from queue import Queue
from time import sleep
import os.path as op
from typing import Tuple

from flask import Flask, request, render_template, Response
from jinja2 import Template
import minify_html

from .module_manager import ModuleManager, ModuleManagerError


APP_DIR = op.dirname(__file__)
STATIC_DIR = op.join(APP_DIR, 'static')
TEMPLATES_DIR = op.join(APP_DIR, 'templates')

WATCH_PERIOD = 0.3
SSE_MESSAGE_TEMPLATE = 'event: file_update\ndata: %s\n\n'


app = Flask(__name__, static_url_path='/static')


def get_static_html(module_manager: ModuleManager, ui_options: dict, minify: bool=True) -> str:
    '''Return the html string of a page that renders the target defined in the module manager.'''

    viewer_css_path = op.join(STATIC_DIR, 'viewer.css')
    viewer_js_path = op.join(STATIC_DIR, 'viewer.js')
    template_path = op.join(TEMPLATES_DIR, 'viewer.html')

    with open(viewer_css_path, encoding='utf-8') as css_file:
        viewer_css = '\n' + css_file.read() + '\n'

    with open(viewer_js_path, encoding='utf-8') as js_file:
        viewer_js = '\n' + js_file.read() + '\n'

    with open(template_path, encoding='utf-8') as template_file:
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
        html = minify_html.minify( # pylint: disable=no-member
            html,
            minify_js=True,
            minify_css=True,
            remove_processing_instructions=True
        )

    return html


def run(port: int, module_manager: ModuleManager, ui_options: dict, is_dead: bool=False) -> None:
    '''Run the Flask web server.'''

    @app.route('/', methods = [ 'GET' ])
    def _root() -> str:
        if module_manager.target_is_dir:
            module_manager.module_name = request.args.get('m')

        return render_template(
            'viewer.html',
            options=ui_options,
            modules_name=module_manager.get_modules_name(),
            data=module_manager.get_data()
        )

    @app.route('/html', methods = [ 'GET' ])
    def _html() -> str:
        if module_manager.target_is_dir:
            module_manager.module_name = request.args.get('m')

        return get_static_html(module_manager, ui_options)

    @app.route('/json', methods = [ 'GET' ])
    def _json() -> Tuple[str, int]:
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
        }, 200

    @app.route('/events', methods = [ 'GET' ])
    def _events() -> Response:
        def stream():
            while True:
                yield events_queue.get()

        return Response(stream(), mimetype='text/event-stream')

    def watchdog() -> None:
        while True:
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

    if not is_dead:
        watchdog_thread = Thread(target=watchdog, daemon=True)
        watchdog_thread.start()

    app.run(host='0.0.0.0', port=port, debug=False)
