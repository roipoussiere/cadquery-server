'''Module ui: define UI class and render functions (show_object, …). Used by the CadQuery script.'''

from cadquery import Color, Assembly


MODEL_COLOR_DEFAULT = Color(0.91, 0.69, 0.14)
MODEL_COLOR_DEBUG   = Color(1, 0, 0, 0.2)


class UI: # pylint: disable=too-few-public-methods
    '''Manage an assembly object composed of all models passed to show_object and debug functions,
    that will be retrieved by CadQuery Server to render it.
    Must be imported by the CadQuery script.'''

    def __init__(self) -> None:
        self.assembly = Assembly()

    def get_assembly(self):
        '''Clear assembly and return the old one.'''

        assembly = self.assembly
        self.assembly = Assembly()
        return assembly


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
