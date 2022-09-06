import json


model_to_show = None # pylint: disable=invalid-name


def show_object(model) -> None:
    global model_to_show # pylint: disable=global-statement, invalid-name
    model_to_show = model


class UI: # pylint: disable=too-few-public-methods

    # pylint: disable=import-outside-toplevel
    @staticmethod
    def get_model() -> list:
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
