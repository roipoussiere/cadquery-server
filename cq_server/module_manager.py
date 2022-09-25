'''Module module_manager: define the ModuleManager and ModuleManagerError classes.'''

import os
import os.path as op
import sys
from typing import List, Dict, Tuple
import glob
import json


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
        self.last_timestamp = 0
        self.available_modules = {}

    def init(self) -> None:
        '''Initialize the module manager, in particular import the CadQuery Python module.'''
        # pylint: disable=unused-import, import-outside-toplevel

        print('Importing CadQuery...', end=' ', flush=True)
        import cadquery
        print('done.')

        sys.path.insert(1, self.modules_dir)
        self.available_modules = self.get_available_modules()

    def get_available_modules(self) -> Dict[str, str]:
        '''Returns a dictionary of available modules as module name: module path'''

        ignored_files_path = self.get_ignored_files_path()

        modules_path = []
        for file_name in os.listdir(self.modules_dir):
            file_path = op.join(self.modules_dir, file_name)
            if op.isfile(file_path) \
                    and op.splitext(file_path)[1] == '.py' \
                    and file_path not in ignored_files_path:
                modules_path.append(file_path)

        return { op.basename(path)[:-3]: path for path in modules_path }

    def get_ignored_files_path(self) -> List[str]:
        '''Update the list of files ignored, based on the .cqsignore file.'''

        ignore_file_path = op.join(self.modules_dir, IGNORE_FILE_NAME)
        ignored_files_path = []

        if op.isfile(ignore_file_path):
            with open(ignore_file_path, encoding='utf-8') as ignore_file:
                for line in ignore_file.readlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ignore = op.join(self.modules_dir, line)
                        ignored_files_path += glob.glob(ignore)

        return ignored_files_path

    def get_most_recent_module(self) -> Tuple[str, str]:
        '''Return the last updated module info as a tuple containing its path and timestamp.'''

        most_recent_module_path = ''
        most_recent_timestamp = 0

        if self.target_is_dir:
            for module_path in self.available_modules.values():
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

        module_path, timestamp = self.get_most_recent_module()
        last_updated = ''

        if self.last_timestamp == 0:
            self.last_timestamp = timestamp

        if self.last_timestamp != timestamp:
            print(f'File { module_path } updated.')
            self.last_timestamp = timestamp
            last_updated = module_path

        return last_updated

    def get_result(self):
        '''Return a CQ assembly object composed of all models passed
        to show_object and debug functions in the CadQuery script.'''

        from cadquery.cqgi import CQModel

        module_script = ''
        with open(self.available_modules[self.module_name], encoding='utf-8') as module_file:
            module_script = module_file.read()

        model = CQModel(module_script)
        result = model.build()

        if not result.success:
            raise ModuleManagerError('Error in model', result.exception)

        return result

    def get_assembly(self):
        from cadquery import Assembly, Color

        results = self.get_result().results

        if not results:
            raise ValueError('nothing to export')

        assembly = Assembly()
        for result in results:
            color = Color(result.options['color']) if 'color' in result.options else None
            assembly.add(result.shape, color=color)

        return assembly

    def get_json_model(self) -> list:
        '''Return the tesselated model of the assembly,
        as a dictionnary usable by three-cad-viewer.'''

        from jupyter_cadquery.cad_objects import to_assembly
        from jupyter_cadquery.base import _tessellate_group
        from jupyter_cadquery.utils import numpy_to_json

        try:
            jcq_assembly = to_assembly(*self.get_assembly().children)
            assembly_tesselated = _tessellate_group(jcq_assembly)
            assembly_json = numpy_to_json(assembly_tesselated)
        except Exception as error:
            raise ModuleManagerError('An error occured when tesselating the assembly.') from error

        return json.loads(assembly_json)

    def get_data(self) -> dict:
        '''Return the data to send to the client, that includes the tesselated model.'''

        data = {}

        if self.module_name:
            try:
                data = {
                    'module_name': self.module_name,
                    'model': self.get_json_model(),
                    'source': ''
                }
            except ModuleManagerError as error:
                if self.should_raise:
                    raise(error)

                data = {
                    'error': error.message,
                    'stacktrace': error.stacktrace
                }

        return data

    def get_ui_instance(self):
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
