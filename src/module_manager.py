import os
import os.path as op
import sys
import traceback
import importlib


class CadQueryModuleManager:
    def __init__(self, modules_path, default_module_name, default_object_var):
        self.default_module_name = default_module_name
        self.default_object_var = default_object_var

        self.module_name = self.default_module_name
        self.object_var = self.default_object_var
        self.modules_path = op.abspath(op.join(os.getcwd(), modules_path))
        self.module = None
        self.last_timestamp = 0

    def init(self):
        print('Importing CadQuery...', end=' ', flush=True)
        import cadquery
        print('done.')

        sys.path.insert(1, self.modules_path)

    def is_file_updated(self):
        if not self.module:
            return False

        timestamp = op.getmtime(self.module.__file__)

        if self.last_timestamp == 0:
            self.last_timestamp = timestamp
            return False

        if timestamp != self.last_timestamp:
            print('File %s updated.' % self.module.__file__)
            self.last_timestamp = timestamp
            return True

    def render_json(self):
        self.load_module()
        model = self.get_model()

        return self.model_to_json(model)

    def model_to_json(self, model):
        from jupyter_cadquery.utils import numpy_to_json
        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group

        return numpy_to_json(_tessellate_group(to_assembly(model)))

    def load_module(self):
        try:
            if self.module and self.module_name == self.module.__name__:
                print('Reloading module %s...' % self.module_name)
                importlib.reload(self.module)
            else:
                print('Importing module %s...' % self.module_name)
                self.module = importlib.import_module(self.module_name)

        except ModuleNotFoundError:
            raise CadQueryModuleManagerError('Can not import module "%s" from %s.'
                % (self.module_name, self.modules_path))

        except Exception as error:
            raise CadQueryModuleManagerError(type(error).__name__ + ': ' + str(error), traceback.format_exc())

    def get_model(self):
        try:
            return getattr(self.module, self.object_var)
        except AttributeError:
            raise CadQueryModuleManagerError('Variable "%s" not found in the module %s.'
                % (self.object_var, self.module_name))


class CadQueryModuleManagerError(Exception):
    def __init__(self, message, stacktrace=''):
        self.message = message
        self.stacktrace = stacktrace

        print(message, file=sys.stderr)
        if stacktrace:
            print(stacktrace, file=sys.stderr)

        super().__init__(self.message)
