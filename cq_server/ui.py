'''Module ui: define UI class and render functions (show_object, …). Used by the CadQuery script.'''

import json
from typing import Tuple


MODEL_OPTIONS_DEFAULT   = { 'color': (232, 176, 36), 'alpha': 1   }
MODEL_OPTIONS_DEBUG = { 'color': (255,   0,  0), 'alpha': 0.2 }


class UI: # pylint: disable=too-few-public-methods
    '''Holds the model to show and allow CadQuery Server to retrieve the tesselated model.
    Must be imported by the CadQuery script.'''

    def __init__(self) -> None:
        self.models_to_show: list = []
        self.color: Tuple[str, str, str] = MODEL_OPTIONS_DEFAULT['color']
        self.alpha: int = MODEL_OPTIONS_DEFAULT['alpha']

    # pylint: disable=import-outside-toplevel
    def get_model(self) -> list:
        '''Return the tesselated model of the object passed in the show_object() function,
        as a dictionnary usable by three-cad-viewer.'''

        from jupyter_cadquery.utils import numpy_to_json
        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group

        if not self.models_to_show:
            return ''

        color = '#{:02x}{:02x}{:02x}{:02x}'.format(*self.color, int(self.alpha*255)) \
            if self.color else None

        assembly = to_assembly(*self.models_to_show, default_color=color)
        tesselated = _tessellate_group(assembly)
        model_json = numpy_to_json(tesselated)
        model = json.loads(model_json)

        return model


ui = UI()


def show_object(*models, options: dict={}) -> None:
    '''Store the given model to ui object in order to allow CadQuery Server to render it.'''

    ui.color = options.get('color', MODEL_OPTIONS_DEFAULT['color'])
    # model.color = color
    ui.alpha = options.get('alpha', MODEL_OPTIONS_DEFAULT['alpha'])
    ui.models_to_show += models


def debug(model) -> None:
    show_object(model, options = MODEL_OPTIONS_DEBUG)
