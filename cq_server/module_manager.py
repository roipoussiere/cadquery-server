'''Module module_manager: define the ModuleManager and ModuleManagerError classes.'''

import os
import os.path as op
import sys
import traceback
import importlib
from typing import List, Tuple
import glob
import inspect
import json

print('Importing CadQuery...', end=' ', flush=True)
import cadquery
print('done.')

from .ui import UI


IGNORE_FILE_NAME = '.cqsignore'


class ModuleManager:
    '''Manage CadQuery scripts (ie. Python modules)'''

    def __init__(self, target: str, should_raise=False):
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

        self.should_raise = should_raise
        self.modules = {}
        self.last_timestamp = 0
        self.ignored_files = []

    def init(self) -> None:
        '''Initialize the module manager, in particular import the CadQuery Python module.'''

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

    def get_assembly(self) -> cadquery.Assembly:
        '''Return a CQ assembly object composed of all models passed
        to show_object and debug functions in the CadQuery script.'''

        self.load_module()
        ui_instance = self.get_ui_instance()
        assembly = ui_instance.get_assembly()

        if not assembly.children:
            raise ModuleManagerError('There is no object to show. Missing show_object()?')

        return assembly

    def get_json_model(self) -> list:
        '''Return the tesselated model of the assembly,
        as a dictionnary usable by three-cad-viewer.'''

        assembly = self.get_assembly()

        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group
        from jupyter_cadquery.utils import numpy_to_json

        try:
            jcq_assembly = to_assembly(*assembly.children)
            assembly_tesselated = _tessellate_group(jcq_assembly)
            assembly_json = numpy_to_json(assembly_tesselated)
        except Exception as error:
            raise ModuleManagerError('An error occured when tesselating the assembly.') from error

        return json.loads(assembly_json)

    def load_module(self) -> None:
        '''Load or reload the `self.module_name` module.'''
        # pylint: disable=broad-except

        if self.module_name not in self.get_modules_name():
            raise ModuleManagerError(f'Module "{ self.module_name }" is not available '
                + 'in the current context.')

        error = None
        if self.module_name in self.modules:
            print(f'Reloading module { self.module_name }...')

            try:
                importlib.reload(self.modules[self.module_name])
            except Exception:
                print('Error when reloading module, trying to re-import it...')

                try:
                    self.modules[self.module_name] = importlib.import_module(self.module_name)
                    importlib.reload(self.modules[self.module_name])
                except Exception as err:
                    error = err

        else:
            print(f'Importing module { self.module_name }...')

            try:
                self.modules[self.module_name] = importlib.import_module(self.module_name)
            except Exception as err:
                error = err

        if error:
            error_message = 'Can not load module. ' + type(error).__name__ + ': ' + str(error)
            raise ModuleManagerError(error_message, traceback.format_exc()) from error

        print('Done.')

    def get_data(self) -> dict:
        '''Return the data to send to the client, that includes the tesselated model.'''

        data = {}

        if self.module_name:
            try:
                data = {
                    'module_name': self.module_name,
                    'model': self.get_json_model(),
                    'source': inspect.getsource(self.modules[self.module_name])
                }
            except ModuleManagerError as error:
                if self.should_raise:
                    raise(error)
                else:
                    data = {
                        'error': error.message,
                        'stacktrace': error.stacktrace
                    }

        return data

    def get_modules_name(self) -> List[str]:
        '''Return the list of available modules name.'''

        return [ op.basename(path)[:-3] for path in self.get_modules_path() ]

    def get_ui_instance(self) -> UI:
        '''Retrieve the ui object imported in the CadQuery script, used to retrieve the model.'''

        try:
            return getattr(self.modules[self.module_name], 'ui')
        except AttributeError as error:
            raise ModuleManagerError('ui is not imported. '
                + 'Please add `from cq_server.ui import ui, show_object` '
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
