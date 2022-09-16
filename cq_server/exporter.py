'''Module renderers: define functions that return things, given a module manager.'''

import os
import os.path as op
import json
import tempfile
from shutil import rmtree

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

    def _saving(self, destination: str, format: str, save: callable):
        if op.dirname(destination) and not op.isdir(op.dirname(destination)):
            os.makedirs(op.dirname(destination))

        save()

        print(f'{ format } file exported in { destination }.')

    def _save_data_to(self, destination: str, format: str, data: str):
        if destination == '-':
            print(data)
        else:
            with open(destination, 'w', encoding='utf-8') as file:
                file.write(data)

    def save_to_html(self, destination: str, ui_options: dict={}, minify: bool=True):
        def save():
            html = self.get_html(ui_options, minify)
            self._save_data_to(destination, 'html', html)

        self._saving(destination, 'html', save)

    def save_to(self, destination: str, format: str):
        def save():
            if format == 'json' :
                self._save_data_to(destination, format, self.get_json())
            elif format == 'js' :
                self._save_data_to(destination, format, self.get_js())
            else:
                self.save(destination, format)

        self._saving(destination, format, save)

    def save(self, destination: str, format: str) -> str:
        '''Save the assembly in the given format.'''

        assembly = self.module_manager.get_assembly()

        if format in [ 'step', 'xml', 'gltf', 'vtkjs', 'vrml' ]:
            assembly.save(destination, exportType=format.upper())
        elif format in [ 'dxf', 'svg', 'stl', 'amf', 'tjs', 'vtp', '3mf' ]:
            exporters.export(assembly.toCompound(), destination, format.upper())
        elif format in [ 'png' , 'pdf' ]:
            with tempfile.NamedTemporaryFile() as svg_file:
                exporters.export(assembly.toCompound(), svg_file.name, 'SVG')
                export = cairosvg.svg2png if format == 'svg' else cairosvg.svg2pdf
                export(file_obj=svg_file, write_to=destination)
        else:
            raise NameError(f'bad export format: { format }')

    def get_json(self) -> str:
        '''Return model data as json string.'''
        
        data = self.module_manager.get_data()
        return json.dumps(data)

    def get_js(self) -> str:
        '''Return model data as js file containing the json.'''

        json_data = self.get_json()
        return f"modules['{ self.module_manager.module_name }'] = { json_data }"

    def get_html(self, ui_options: dict, minify: bool=True) -> str:
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

    def build_website(self, destination: str, ui_options: dict, minify=False):
        '''Build static website containing index page and static files for all modules.'''

        if op.isdir(destination):
            rmtree(destination)

        self.save_to_html(op.join(destination, 'index.html'), ui_options, minify)

        js_path = op.join(destination, 'js')
        png_path = op.join(destination, 'png')
        stl_path = op.join(destination, 'stl')

        for module_name in self.module_manager.get_modules_name():
            self.module_manager.module_name = module_name

            self.save_to(op.join(js_path, f'{ module_name }.js'), 'js')
            self.save_to(op.join(png_path, f'{ module_name }.png'), 'png')
            self.save_to(op.join(stl_path, f'{ module_name }.stl'), 'stl')
