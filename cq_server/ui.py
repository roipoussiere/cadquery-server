'''Module ui: define show_object() function and UI class, used by the CadQuery script.'''

import json


model_to_show = None # pylint: disable=invalid-name


def show_object(model) -> None:
    '''Store the given model in order to allow CadQuery Server to render it when necessary.'''

    global model_to_show # pylint: disable=global-statement, invalid-name
    model_to_show = model


class UI: # pylint: disable=too-few-public-methods
    '''Static class that must be imported by the CadQuery script to allow CadQuery Server to
    retrieve the model to show, stored globally.
    Static is used here to avoid instanciating the class on the CadQuery script.'''

    # pylint: disable=import-outside-toplevel
    @staticmethod
    def get_model() -> list:
        '''Return the tesselated model of the object passed in the show_object() function,
        as a dictionnary usable by three-cad-viewer.'''

        from jupyter_cadquery.utils import numpy_to_json
        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group

        if not model_to_show:
            return ''

        assembly = to_assembly(model_to_show)
        tesselated = _tessellate_group(assembly)
        model_json = numpy_to_json(tesselated)
        model = json.loads(model_json)

        return model
