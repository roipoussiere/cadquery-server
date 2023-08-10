'''Module server: used to run the Flask web server.'''

import json
from threading import Thread
from queue import Queue
from time import sleep
import os.path as op
from typing import Tuple

from flask import Flask, request, render_template, make_response, Response, send_file, abort

from .module_manager import ModuleManager


WATCH_PERIOD = 0.3
SSE_MESSAGE_TEMPLATE = 'event: file_update\ndata: %s\n\n'


app = Flask(__name__, static_url_path='/static')


def run(port: int, module_manager: ModuleManager, ui_options: dict, is_dead: bool=False) -> None:
    '''Run the Flask web server.'''

    @app.route('/', methods = [ 'GET' ])
    def _root() -> str:
        if module_manager.target_is_dir:
            module_manager.module_name = request.args.get('m')

        return render_template(
            'viewer.html',
            options=ui_options,
            modules_name=list(module_manager.available_modules.keys()),
            data=module_manager.get_data()
        )

    @app.route('/html', methods = [ 'GET' ])
    def _html() -> str:
        # pylint: disable=import-outside-toplevel

        from .exporter import Exporter

        if module_manager.target_is_dir:
            module_manager.module_name = request.args.get('m')

        exporter = Exporter(module_manager)
        return exporter.get_html(ui_options)

    @app.route('/download', methods = [ 'GET' ])
    def _download() -> Response:
        '''Export specified module in the requested format and send it to the requester'''
        module = request.args.get("m")
        if module is None or module not in module_manager.get_available_modules().keys():
            abort(Response("Module not found", 400))

        from .exporter import Exporter
        exporter = Exporter(module_manager)
        file_format = request.args.get("format")
        if file_format is None or file_format not in exporter.valid_export_formats:
            abort(Response("File format not supported", 400))

        try:
            exported_file = exporter.export(module, file_format)
            return send_file(exported_file, as_attachment=True)
        except FileNotFoundError:
            abort(500)


    @app.route('/json', methods = [ 'GET' ])
    def _json() -> Tuple[str, int]:
        if module_manager.target_is_dir:
            module_manager.module_name = request.args.get('m')

        data = module_manager.get_data()
        return data, (400 if 'error' in data else 200)

    @app.route('/events', methods = [ 'GET' ])
    def _events() -> Response:
        def stream():
            while True:
                data = events_queue.get()
                print(f'Sending Server Sent Event: { data[:100] }...')
                yield data

        response = make_response(stream())
        response.mimetype = 'text/event-stream'
        response.headers['Cache-Control'] = 'no-store, must-revalidate'
        response.headers['Expires'] = 0
        return response

    def watchdog() -> None:
        while True:
            last_updated_file = module_manager.get_last_updated_file()

            if last_updated_file:
                module_manager.module_name = op.basename(last_updated_file)[:-3]
                data = module_manager.get_data()
                events_queue.put(SSE_MESSAGE_TEMPLATE % json.dumps(data))
            sleep(WATCH_PERIOD)

    events_queue = Queue(maxsize = 3)
    module_manager.init()

    if not is_dead:
        watchdog_thread = Thread(target=watchdog, daemon=True)
        watchdog_thread.start()

    app.run(host='0.0.0.0', port=port, debug=False)
