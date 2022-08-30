import os
import sys
import traceback
import importlib


class CadQueryModuleManager:
    def __init__(self, dir, main, model_var, output):
        self.dir = dir
        self.main = main
        self.model_var = model_var
        self.output = output

        self.module = None

    def init(self):
        print('Importing CadQuery...', end=' ', flush=True)
        import cadquery
        print('done.')

        modules_path = os.path.abspath(os.path.join(os.getcwd(), self.dir))
        sys.path.insert(1, modules_path)

    def render(self, module_name, output):
        if not module_name:
            module_name = self.main
        if not output:
            output = self.output

        self.load_module(module_name)
        model = self.get_model()

        if output == 'json':
            return self.render_json(model)
        else:
            raise CadQueryModuleManagerError('Output format "%s" is not supported.' % output)

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

    def get_model(self):
        try:
            return getattr(self.module, self.model_var)
        except AttributeError:
            raise CadQueryModuleManagerError('Variable "%s" is required to render the model.' % self.model_var)


class CadQueryModuleManagerError(Exception):
    def __init__(self, message, stacktrace=''):
        self.message = message
        self.stacktrace = stacktrace

        print(message, file=sys.stderr)
        if stacktrace:
            print(stacktrace, file=sys.stderr)

        super().__init__(self.message)
