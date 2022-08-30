import os
import sys
import traceback
import importlib
import threading


WATCH_PERIOD = 0.5


class CadQueryModuleManager:
    def __init__(self, dir, default_module_name, default_object_var, default_format):
        self.dir = dir
        self.default_module_name = default_module_name
        self.default_object_var = default_object_var
        self.default_format = default_format

        self.module = None
        self.watching_file = ''
        self.last_timestamp = 0

    def update_watching_file(self, module_name):
        self.watching_file = os.path.join(self.dir, module_name + '.py')

    def init(self):
        print('Importing CadQuery...', end=' ', flush=True)
        import cadquery
        print('done.')

        modules_path = os.path.abspath(os.path.join(os.getcwd(), self.dir))
        sys.path.insert(1, modules_path)

        self.check_file()

    def check_file(self):
        if self.watching_file:
            timestamp = os.stat(self.watching_file).st_mtime
            if timestamp != self.last_timestamp:
                if self.last_timestamp != 0:
                    print('File %s updated.' % self.watching_file)
                self.last_timestamp = timestamp
        threading.Timer(WATCH_PERIOD, self.check_file).start()

    def render(self, module_name, object_var, format):
        if not module_name:
            module_name = self.default_module_name
        if not object_var:
            object_var = self.default_object_var
        if not format:
            format = self.default_format

        self.update_watching_file(module_name)
        self.load_module(module_name)
        model = self.get_model(object_var)

        if format == 'json':
            return self.model_to_json(model)
        else:
            raise CadQueryModuleManagerError('Output format "%s" is not supported.' % format)

    def model_to_json(self, model):
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
