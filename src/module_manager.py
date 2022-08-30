import os
import sys
import traceback
import importlib


class CadQueryModuleManager:
    def __init__(self, dir, default_module_name, default_object_var, default_format):
        self.dir = dir
        self.default_module_name = default_module_name
        self.default_object_var = default_object_var
        self.default_format = default_format

        self.module = None

    def init(self):
        print('Importing CadQuery...', end=' ', flush=True)
        import cadquery
        print('done.')

        modules_path = os.path.abspath(os.path.join(os.getcwd(), self.dir))
        sys.path.insert(1, modules_path)

    def render(self, module_name, object_var, format):
        if not module_name:
            module_name = self.default_module_name
        if not object_var:
            object_var = self.default_object_var
        if not format:
            format = self.default_format

        self.load_module(module_name)
        model = self.get_model(object_var)

        if format == 'json':
            return self.render_json(model)
        else:
            raise CadQueryModuleManagerError('Output format "%s" is not supported.' % format)

    def render_json(self, model):
        from jupyter_cadquery.utils import numpy_to_json
        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group

        return numpy_to_json(_tessellate_group(to_assembly(model)))

    def load_module(self, module_name):
        try:
            if self.module:
                print('Reloading module %s...' % module_name)
                importlib.reload(self.module)
            else:
                print('Importing module %s...' % module_name)
                self.module = importlib.import_module(module_name)

        except ModuleNotFoundError:
            raise CadQueryModuleManagerError('Can not import module "%s".' % module_name)

        except Exception as error:
            raise CadQueryModuleManagerError(type(error).__name__ + ': ' + str(error), traceback.format_exc())

    def get_model(self, model_var):
        try:
            return getattr(self.module, model_var)
        except AttributeError:
            raise CadQueryModuleManagerError('3d object variable "%s" is not found in the module.' % self.default_object_var)


class CadQueryModuleManagerError(Exception):
    def __init__(self, message, stacktrace=''):
        self.message = message
        self.stacktrace = stacktrace

        print(message, file=sys.stderr)
        if stacktrace:
            print(stacktrace, file=sys.stderr)

        super().__init__(self.message)
