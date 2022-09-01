import os
import os.path as op
import sys
import traceback
import importlib


class CadQueryModuleManager:
    def __init__(self, modules_path, default_module_name):
        self.modules_path = op.abspath(op.join(os.getcwd(), modules_path))
        self.default_module_name = default_module_name

        self.module_name = self.default_module_name
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

    def get_model(self):
        self.load_module()

        UI = self.get_ui_class()
        model = UI.get_model()

        if not model:
            raise CadQueryModuleManagerError('There is no object to show. Missing show_object() ?')

        return model

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

    def get_ui_class(self):
        try:
            return getattr(self.module, 'UI')
        except AttributeError:
            raise CadQueryModuleManagerError('UI class is not imported. '
                + 'Please add `from cq_server.ui import UI, show_object` '
                + 'at the begining of the script.')


class CadQueryModuleManagerError(Exception):
    def __init__(self, message, stacktrace=''):
        self.message = message
        self.stacktrace = stacktrace

        print(message, file=sys.stderr)
        if stacktrace:
            print(stacktrace, file=sys.stderr)

        super().__init__(self.message)
