import os
import os.path as op
import sys
import traceback
import importlib


class ModuleManager:
    def __init__(self, target):
        if op.isfile(target):
            self.modules_dir = op.abspath(op.dirname(target))
            self.main_module_name = op.basename(target[:-3])
        elif op.isdir(target):
            self.modules_dir = op.abspath(target)
            self.main_module_name = '__index__'
        else:
            raise ModuleManagerError('No file or folder found at "%s".' % target)

        self.module_name = self.main_module_name
        self.module = None
        self.last_timestamp = 0

    def init(self):
        print('Importing CadQuery...', end=' ', flush=True)
        import cadquery
        print('done.')

        sys.path.insert(1, self.modules_dir)

    def get_available_modules(self):
        modules_name = []
        for file_name in os.listdir(self.modules_dir):
            file_path = op.join(self.modules_dir, file_name)
            if op.isfile(file_path) and op.splitext(file_path)[1] == '.py':
                modules_name.append(op.basename(file_name[:-3]))
        return modules_name

    def set_module_name(self, module_name):
        self.module_name = self.main_module_name if not module_name else module_name

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
            raise ModuleManagerError('There is no object to show. Missing show_object() ?')

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
            raise ModuleManagerError('Can not import module "%s" from %s.'
                % (self.module_name, self.modules_dir))

        except Exception as error:
            raise ModuleManagerError(type(error).__name__ + ': ' + str(error), traceback.format_exc())

    def get_ui_class(self):
        try:
            return getattr(self.module, 'UI')
        except AttributeError:
            raise ModuleManagerError('UI class is not imported. '
                + 'Please add `from cq_server.ui import UI, show_object` '
                + 'at the begining of the script.')


class ModuleManagerError(Exception):
    def __init__(self, message, stacktrace=''):
        self.message = message
        self.stacktrace = stacktrace

        print('Module manager error: ' + message, file=sys.stderr)
        if stacktrace:
            print(stacktrace, file=sys.stderr)

        super().__init__(self.message)
