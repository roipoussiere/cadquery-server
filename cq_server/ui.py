'''Module ui: define UI class and render functions (show_object, …). Used by the CadQuery script.'''

import json
from cadquery import Color, Assembly


MODEL_COLOR_DEFAULT = Color(0.91, 0.69, 0.14)
MODEL_COLOR_DEBUG   = Color(1, 0, 0, 0.2)


class UI: # pylint: disable=too-few-public-methods
    '''Holds the model to show and allow CadQuery Server to retrieve the tesselated model.
    Must be imported by the CadQuery script.'''

    def __init__(self) -> None:
        self.assembly = Assembly()

    # pylint: disable=import-outside-toplevel
    def get_model(self) -> list:
        '''Return the tesselated model of the object passed in the show_object() function,
        as a dictionnary usable by three-cad-viewer.'''

        if not self.assembly.children:
            return ''

        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group
        from jupyter_cadquery.utils import numpy_to_json

        assembly = to_assembly(*self.assembly.children)
        assembly_tesselated = _tessellate_group(assembly)
        assembly_json = numpy_to_json(assembly_tesselated)
        assembly_dict = json.loads(assembly_json)

        self.clear()
        return assembly_dict

    def clear(self):
        '''Clear assembly.'''

        self.assembly = Assembly()


ui = UI()


def show_object(*models, name: str|None=None, options: dict={}) -> None:
    '''Add the given model(s) to ui assembly in order to allow CadQuery Server to render it.'''

    rgb = options.get('color', None)
    alpha = options.get('alpha', None)

    color = rgb          if type(rgb) == Color \
        else Color(rgb)  if type(rgb) == str \
        else Color(*rgb) if type(rgb) == tuple \
        else MODEL_COLOR_DEFAULT

    if alpha:
        color = Color(color.toTuple()[:3] + [ alpha ])

    for counter, model in enumerate(models):
        _name = f'{ name }_{ counter }' if name and len(models) > 1 else name
        ui.assembly.add(model, name=_name, color=color)


def debug(model, name: str|None=None) -> None:
    '''Same as show_object() but with the predefined debug color.'''

    show_object(model, name=name, options={ 'color': MODEL_COLOR_DEBUG })
