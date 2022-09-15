'''Module renderers: define functions that return things, given a module manager.'''

import os.path as op
import json
import tempfile

from jinja2 import Template
import minify_html
from cadquery import exporters
import cairosvg
from .module_manager import ModuleManager


APP_DIR = op.dirname(__file__)
STATIC_DIR = op.join(APP_DIR, 'static')
TEMPLATES_DIR = op.join(APP_DIR, 'templates')

class Exporter:
    def __init__(self, module_manager: ModuleManager):
        self.module_manager = module_manager
        self.module_manager.init()

    def to_json(self) -> str:
        '''Return model data as json string'''
        
        data = self.module_manager.get_data()
        return json.dumps(data)

    def save(self, path: str, format: str) -> str:
        '''Save the assembly in the given format.'''

        assembly = self.module_manager.get_assembly()

        if format in [ 'STEP', 'XML', 'GLTF', 'VTKJS', 'VRML' ]:
            assembly.save(path, exportType=format)
        elif format in [ 'DXF', 'SVG', 'STL', 'AMF', 'TJS', 'VTP', '3MF' ]:
            exporters.export(assembly.toCompound(), path, format)
        elif format in [ 'PNG' , 'PDF' ]:
            with tempfile.NamedTemporaryFile() as svg_file:
                exporters.export(assembly.toCompound(), svg_file.name, 'SVG')
                export = cairosvg.svg2png if format == 'PNG' else cairosvg.svg2pdf
                export(file_obj=svg_file, write_to=path)
        else:
            raise NameError('bad format')

    def to_html(self, ui_options: dict, minify: bool=True) -> str:
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

        html = template.render(
            static=True,
            viewer_css=viewer_css,
            viewer_js=viewer_js,
            options=ui_options,
            modules_name=self.module_manager.get_modules_name(),
            data=self.module_manager.get_data()
        )

        if minify:
            html = minify_html.minify( # pylint: disable=no-member
                html,
                minify_js=True,
                minify_css=True,
                remove_processing_instructions=True
            )

        return html
