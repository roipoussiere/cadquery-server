'''Module ui: define UI class and render functions (show_object, …). Used by the CadQuery script.'''

import json
from typing import List
from jupyter_cadquery.utils import numpy_to_json, Color


MODEL_OPTIONS_DEFAULT   = { 'color': (232, 176, 36), 'alpha': 1   }
MODEL_OPTIONS_DEBUG = { 'color': (255,   0,  0), 'alpha': 0.2 }


class UI: # pylint: disable=too-few-public-methods
    '''Holds the model to show and allow CadQuery Server to retrieve the tesselated model.
    Must be imported by the CadQuery script.'''

    def __init__(self) -> None:
        self.names: List[str] = []
        self.models: list = []
        self.colors: List[Color] = []

    # pylint: disable=import-outside-toplevel
    def get_model(self) -> list:
        '''Return the tesselated model of the object passed in the show_object() function,
        as a dictionnary usable by three-cad-viewer.'''

        if not self.models:
            return ''

        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group

        assembly = to_assembly(*self.models, names=self.names)
        for idx, obj in enumerate(assembly.objects):
            if hasattr(obj, 'color'):
                obj.color = self.colors[idx]

        assembly_tesselated = _tessellate_group(assembly)
        assembly_json = numpy_to_json(assembly_tesselated)
        assembly_dict = json.loads(assembly_json)

        self.clear()
        return assembly_dict

    def clear(self):
        '''Clear all data stored in the UI instance.'''

        self.names  = []
        self.models = []
        self.colors = []


ui = UI()


def show_object(*models, name: str=None, options: dict={}) -> None:
    '''Store the given model to ui object in order to allow CadQuery Server to render it.'''

    rgb = options.get('color', MODEL_OPTIONS_DEFAULT['color'])
    alpha = options.get('alpha', MODEL_OPTIONS_DEFAULT['alpha'])
    color = Color('#{:02x}{:02x}{:02x}{:02x}'.format(*rgb, int(alpha*255)))

    for model in models:
        ui.names.append(name)
        ui.models.append(model)
        ui.colors.append(color)


def debug(model, name: str = None) -> None:
    '''Same as show_object() but with predefined debug color and alpha used for debugging.'''

    show_object(model, name=name, options = MODEL_OPTIONS_DEBUG)
