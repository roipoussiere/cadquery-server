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
DEFAULT_SVG_OPTIONS = {
    'width': 50,
    'height': 50,
    'marginLeft': 5,
    'marginTop': 5,
    'showAxes': False,
    'strokeColor': (50, 50, 50),
    'hiddenColor': (100, 100, 100),
    'showHidden': True,
    'backgroundColor': '#aaa' # used for rasterization
}


class Exporter:
    '''Class used to export the target in many formats.'''

    def __init__(self, module_manager: ModuleManager):
        self.module_manager = module_manager
        self.module_manager.init()

    def _saving(self, destination: str, file_format: str, save: callable):
        if op.dirname(destination) and not op.isdir(op.dirname(destination)):
            os.makedirs(op.dirname(destination))

        save()

        print(f'{ file_format } file exported in { destination }.')

    def _save_data_to(self, destination: str, data: str):
        if destination == '-':
            print(data)
        else:
            with open(destination, 'w', encoding='utf-8') as file:
                file.write(data)

    def _save(self, destination: str, file_format: str, options=None) -> str:
        '''Save the assembly in the given format.'''

        assembly = self.module_manager.get_assembly()
        if not options and file_format in [ 'svg', 'png', 'pdf' ]:
            options = DEFAULT_SVG_OPTIONS

        if file_format in [ 'step', 'xml', 'gltf', 'vtkjs', 'vrml' ]:
            assembly.save(destination, exportType=file_format.upper())
        elif file_format in [ 'dxf', 'svg', 'stl', 'amf', 'tjs', 'vtp', '3mf' ]:
            exporters.export(assembly.toCompound(), destination, file_format.upper(), opt=options)
        elif file_format in [ 'png' , 'pdf' ]:
            with tempfile.NamedTemporaryFile() as svg_file:
                exporters.export(assembly.toCompound(), svg_file.name, 'SVG', opt=options)
                if file_format == 'png':
                    cairosvg.svg2png(file_obj=svg_file, write_to=destination, scale=2,
                        background_color=options.get('backgroundColor', None))
                else:
                    cairosvg.svg2pdf(file_obj=svg_file, write_to=destination)
        else:
            raise NameError(f'bad export format: { file_format }')

    def save_to_html(self, destination: str, ui_options: dict, minify: bool=True):
        '''Save a static html page that renders the assembly.'''

        def save():
            html = self.get_html(ui_options, minify)
            self._save_data_to(destination, html)

        self._saving(destination, 'html', save)

    def save_to(self, destination: str, file_format: str):
        '''Save the assembly in the given format, including json and js.'''

        def save():
            if file_format == 'json' :
                self._save_data_to(destination, self.get_json())
            elif file_format == 'js' :
                self._save_data_to(destination, self.get_js())
            else:
                self._save(destination, file_format)

        self._saving(destination, file_format, save)

    def get_json(self) -> str:
        '''Return assembly data as json string.'''

        data = self.module_manager.get_data()
        return json.dumps(data)

    def get_js(self) -> str:
        '''Return assembly data as js file containing the json.'''

        json_data = self.get_json()
        return f"modules['{ self.module_manager.module_name }'] = { json_data }"

    def get_html(self, ui_options: dict, minify: bool=True) -> str:
        '''Return the html string of a page that renders the assembly.'''

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
