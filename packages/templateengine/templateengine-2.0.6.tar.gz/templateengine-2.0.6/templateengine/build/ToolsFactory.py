from pip_services4_components.build import Factory
from pip_services4_components.refer import Descriptor
from ..exec.tools import CopyAllTool, CopyDirTool, CreateDirTool, RenameDirTool, DeleteDirTool
from ..exec.tools import CopyFileTool, CreateFileTool, RenameFileTool, DeleteFileTool, EditContentTool

class ToolsFactory(Factory):
    __CopyAllToolDescriptor = Descriptor('templateengine-v2', 'tool', '*', 'copy-all', '1.0')
    __CopyDirToolDescriptor = Descriptor('templateengine-v2', 'tool', '*', 'copy-dir', '1.0')
    __CreateDirToolDescriptor = Descriptor('templateengine-v2', 'tool', '*', 'create-dir', '1.0')
    __RenameDirToolDescriptor = Descriptor('templateengine-v2', 'tool', '*', 'rename-dir', '1.0')
    __DeleteDirToolDescriptor = Descriptor('templateengine-v2', 'tool', '*', 'delete-dir', '1.0')
    __CopyFileToolDescriptor = Descriptor('templateengine-v2', 'tool', '*', 'copy-file', '1.0')
    __CreateFileToolDescriptor = Descriptor('templateengine-v2', 'tool', '*', 'create-file', '1.0')
    __RenameFileToolDescriptor = Descriptor('templateengine-v2', 'tool', '*', 'rename-file', '1.0')
    __DeleteFileToolDescriptor = Descriptor('templateengine-v2', 'tool', '*', 'delete-file', '1.0')
    __EditContentToolDescriptor = Descriptor('templateengine-v2', 'tool', '*', 'edit-content', '1.0')

    def __init__(self):
        super().__init__()

        self.register_as_type(self.__CopyAllToolDescriptor, CopyAllTool)
        self.register_as_type(self.__CopyDirToolDescriptor, CopyDirTool)
        self.register_as_type(self.__CreateDirToolDescriptor, CreateDirTool)
        self.register_as_type(self.__RenameDirToolDescriptor, RenameDirTool)
        self.register_as_type(self.__DeleteDirToolDescriptor, DeleteDirTool)
        self.register_as_type(self.__CopyFileToolDescriptor, CopyFileTool)
        self.register_as_type(self.__CreateFileToolDescriptor, CreateFileTool)
        self.register_as_type(self.__RenameFileToolDescriptor, RenameFileTool)
        self.register_as_type(self.__DeleteFileToolDescriptor, DeleteFileTool)
        self.register_as_type(self.__EditContentToolDescriptor, EditContentTool)