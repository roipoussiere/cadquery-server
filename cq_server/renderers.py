'''Module renderers: define functions that return things, given a module manager.'''

import os.path as op

from jinja2 import Template
import minify_html

from .module_manager import ModuleManager


APP_DIR = op.dirname(__file__)
STATIC_DIR = op.join(APP_DIR, 'static')
TEMPLATES_DIR = op.join(APP_DIR, 'templates')


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
