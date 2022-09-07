'''Module ui: define UI class and render functions (show_object, …). Used by the CadQuery script.'''

import json


class UI: # pylint: disable=too-few-public-methods
    '''Holds the model to show and allow CadQuery Server to retrieve the tesselated model.
    Must be imported by the CadQuery script.'''

    def __init__(self) -> None:
        self.model_to_show = None

    # pylint: disable=import-outside-toplevel
    def get_model(self) -> list:
        '''Return the tesselated model of the object passed in the show_object() function,
        as a dictionnary usable by three-cad-viewer.'''

        from jupyter_cadquery.utils import numpy_to_json
        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group

        if not self.model_to_show:
            return ''

        assembly = to_assembly(self.model_to_show)
        tesselated = _tessellate_group(assembly)
        model_json = numpy_to_json(tesselated)
        model = json.loads(model_json)

        return model


ui = UI()


def show_object(model) -> None:
    '''Store the given model to ui object in order to allow CadQuery Server to render it.'''

    ui.model_to_show = model
