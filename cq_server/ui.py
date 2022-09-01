import json

object_to_show = None


def show_object(object):
    global object_to_show
    object_to_show = object


class UI:

    @staticmethod
    def get_model():
        from jupyter_cadquery.utils import numpy_to_json
        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group

        if not object_to_show:
            return ''

        assembly = to_assembly(object_to_show)
        tesselated = _tessellate_group(assembly)
        model_json = numpy_to_json(tesselated)
        model = json.loads(model_json)

        return model
