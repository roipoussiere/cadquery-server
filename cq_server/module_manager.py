'''Module module_manager: define the ModuleManager and ModuleManagerError classes.'''

import os
import os.path as op
import sys
import traceback
import importlib
from typing import List, Tuple
import glob


IGNORE_FILE_NAME = '.cqsignore'


class ModuleManager:
    '''Manage CadQuery scripts (ie. Python modules)'''

    def __init__(self, target: str):
        if op.isfile(target):
            self.target_is_dir = False
            self.modules_dir = op.abspath(op.dirname(target))
            self.module_name = op.basename(target[:-3])
        elif op.isdir(target):
            self.target_is_dir = True
            self.modules_dir = op.abspath(target)
            self.module_name = None
        else:
            raise ModuleManagerError(f'No file or folder found at "{ target }".')

        self.modules = {}
        self.last_timestamp = 0
        self.ignored_files = []

    def init(self) -> None:
        '''Initialize the module manager, in particular import the CadQuery Python module.'''

        print('Importing CadQuery...', end=' ', flush=True)
        import cadquery # pylint: disable=import-outside-toplevel, unused-import
        print('done.')

        sys.path.insert(1, self.modules_dir)
        self.update_ignore_list()

    def update_ignore_list(self) -> None:
        '''Update the list of files ignored, based on the .cqsignore file.'''

        ignore_file_path = op.join(self.modules_dir, IGNORE_FILE_NAME)

        if op.isfile(ignore_file_path):
            with open(ignore_file_path, encoding='utf-8') as ignore_file:
                for line in ignore_file.readlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ignore = op.join(self.modules_dir, line)
                        self.ignored_files += glob.glob(ignore)

    def get_modules_path(self) -> List[str]:
        '''Returns the list of available modules'''

        modules_path = []
        for file_name in os.listdir(self.modules_dir):
            file_path = op.join(self.modules_dir, file_name)
            if op.isfile(file_path) \
                    and op.splitext(file_path)[1] == '.py' \
                    and file_path not in self.ignored_files:
                modules_path.append(file_path)
        return modules_path

    def get_most_recent_module_info(self) -> Tuple[str, str]:
        '''Return the last updated module info as a tuple containing its path and timestamp.'''

        most_recent_module_path = ''
        most_recent_timestamp = 0

        if self.target_is_dir:
            for module_path in self.get_modules_path():
                timestamp = op.getmtime(module_path)
                if timestamp > most_recent_timestamp:
                    most_recent_module_path = module_path
                    most_recent_timestamp = timestamp
        else:
            most_recent_module_path = op.join(self.modules_dir, self.module_name + '.py')
            most_recent_timestamp = op.getmtime(most_recent_module_path)

        return most_recent_module_path, most_recent_timestamp

    def get_last_updated_file(self) -> str:
        '''If a file has been updated since the last call of this function call,
        return its path, otherwise return an empty string.'''

        module_path, timestamp = self.get_most_recent_module_info()
        last_updated = ''

        if self.last_timestamp == 0:
            self.last_timestamp = timestamp

        if self.last_timestamp != timestamp:
            print(f'File { module_path } updated.')
            self.last_timestamp = timestamp
            last_updated = module_path

        return last_updated

    def get_model(self) -> list:
        '''Return the tesselated model of the object passed in the show_object() function in the
        user script, as a dictionnary usable by three-cad-viewer.'''

        self.load_module()

        ui_class = self.get_ui_class()
        model = ui_class.get_model()

        if not model:
            raise ModuleManagerError('There is no object to show. Missing show_object()?')

        return model

    def load_module(self) -> None:
        '''Load or reload the `self.module_name` module.'''

        if self.module_name not in self.get_modules_name():
            raise ModuleManagerError(f'Module "{ self.module_name }" is not available '
                + 'in the current context.')

        try:
            if self.module_name in sys.modules:
                print(f'Reloading module { self.module_name }...')
                importlib.reload(self.modules[self.module_name])
            else:
                print(f'Importing module { self.module_name }...')
                self.modules[self.module_name] = importlib.import_module(self.module_name)

        except Exception as error:
            error_message = type(error).__name__ + ': ' + str(error)
            raise ModuleManagerError(error_message, traceback.format_exc()) from error

    def get_data(self) -> dict:
        '''Return the data to send to the client, that includes the tesselated model.'''

        data = {}

        if self.module_name:
            try:
                data = {
                    'module_name': self.module_name,
                    'model': self.get_model()
                }
            except ModuleManagerError as error:
                data={
                    'error': error.message,
                    'stacktrace': error.stacktrace
                }

        return data

    def get_modules_name(self) -> List[str]:
        '''Return the list of available modules name.'''

        return [ op.basename(path)[:-3] for path in self.get_modules_path() ]

    def get_ui_class(self) -> type:
        '''Retrieve the UI class imported in the user CadQuery script, used to get the model.'''

        try:
            return getattr(self.modules[self.module_name], 'UI')
        except AttributeError as error:
            raise ModuleManagerError('UI class is not imported. '
                + 'Please add `from cq_server.ui import UI, show_object` '
                + 'at the begining of the script.') from error


class ModuleManagerError(Exception):
    '''Error class used to define ModuleManager errors.'''

    def __init__(self, message: str, stacktrace: str=''):
        self.message = message
        self.stacktrace = stacktrace

        print('Module manager error: ' + message, file=sys.stderr)
        if stacktrace:
            print(stacktrace, file=sys.stderr)

        super().__init__(self.message)
