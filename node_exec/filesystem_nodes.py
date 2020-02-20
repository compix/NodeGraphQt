from node_exec.base_nodes import defNode, VariableInputCountNode, BaseCustomCodeNode
from node_exec import code_generator
import shutil
import os
import distutils
from distutils import dir_util

IDENTIFIER = "Filesystem"

@defNode("Join Paths", returnNames=["path"], identifier=IDENTIFIER)
def joinPaths(*args):
    return os.path.join(*args)

@defNode("Copy Directory", isExecutable=True, identifier=IDENTIFIER)
def copyDirectory(srcPath, dstPath):
    distutils.dir_util.copy_tree(srcPath, dstPath)

@defNode("Copy File", isExecutable=True, identifier=IDENTIFIER)
def copyFile(srcPath, dstPath):
    shutil.copy2(srcPath, dstPath)

@defNode("Move File or Directory", isExecutable=True, identifier=IDENTIFIER)
def moveFileOrDirectory(srcPath, dstPath):
    shutil.move(srcPath, dstPath)

@defNode("Remove File", isExecutable=True, identifier=IDENTIFIER)
def removeFile(filePath):
    os.remove(filePath)

@defNode("Remove Directory", isExecutable=True, identifier=IDENTIFIER)
def removeDirectory(dirPath):
    distutils.dir_util.remove_tree(dirPath)

@defNode("Create Directory", isExecutable=True, identifier=IDENTIFIER)
def createDirectory(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

@defNode("Path Exists", identifier=IDENTIFIER)
def pathExists(path):
    return os.path.exists(path)

@defNode("Is File", identifier=IDENTIFIER)
def isFile(path):
    return os.path.isfile(path)

@defNode("Is Directory", identifier=IDENTIFIER)
def isDirectory(path):
    return os.path.isdir(path)

@defNode("Path Basename", identifier=IDENTIFIER)
def getPathBasename(path):
    return os.path.basename(path)

@defNode("Path Directory", identifier=IDENTIFIER)
def getPathDirName(path):
    return os.path.dirname(path)

@defNode("File Extension", identifier=IDENTIFIER)
def getFileExtension(filePath):
    return os.path.splitext(filePath)[1]

class FileAndDirectoryWalker(BaseCustomCodeNode):
        __identifier__ = IDENTIFIER
        NODE_NAME = 'Walk Files And Directories'

        def __init__(self):
            super().__init__()

            self.add_exec_input('Execute')

            self.loop_body_port = self.add_exec_output('Iteration')
            self.loop_complete_port = self.add_exec_output('Completed')

            self.add_output('root')
            self.add_output('dirs')
            self.add_output('files')

            self.add_input('directory')

        @property
        def importLines(self):
            return ["import os"]

        def generateCode(self, sourceCodeLines, indent):
            inputParams = code_generator.getInputParamsSource(self)

            # Loop body code:
            loopVarRoot = code_generator.getVarNameSource(self, idx=0)
            loopVarDirs = code_generator.getVarNameSource(self, idx=1)
            loopVarFiles = code_generator.getVarNameSource(self, idx=2)

            walkStatement = f"os.walk({inputParams[0]})"
            loopConditionCode = code_generator.makeCodeLine(f"for {loopVarRoot},{loopVarDirs},{loopVarFiles} in {walkStatement}:", indent)

            code_generator.expandCodeWithCondition(self.loop_body_port, sourceCodeLines, loopConditionCode, indent)

            # Loop completion code:
            code_generator.expandExecCode(self.loop_complete_port, sourceCodeLines, indent)

class FileWalker(BaseCustomCodeNode):
        __identifier__ = IDENTIFIER
        NODE_NAME = 'Walk Files'

        def __init__(self):
            super().__init__()

            self.add_exec_input('Execute')

            self.loop_body_port = self.add_exec_output('Iteration')
            self.loop_complete_port = self.add_exec_output('Completed')

            self.add_output('filePath')
            self.add_input('directory')

        @property
        def importLines(self):
            return ["import os"]

        def generateCode(self, sourceCodeLines, indent):
            inputParams = code_generator.getInputParamsSource(self)

            # Loop body code:
            loopVarFile = code_generator.getVarNameSource(self, idx=0)
            loopVarRoot = code_generator.getVarNameSource(self, idx=1)
            loopVarFiles = code_generator.getVarNameSource(self, idx=2)

            walkStatement = f"os.walk({inputParams[0]})"
            loopConditionCode = code_generator.makeCodeLine(f"for {loopVarRoot},_,{loopVarFiles} in {walkStatement}:", indent)
            sourceCodeLines.append(loopConditionCode)
            innerLoopConditionCode = code_generator.makeCodeLine(f"for {loopVarFile} in {loopVarFiles}:", indent + code_generator.DEFAULT_INDENT)
            preBodyLines = [code_generator.makeCodeLine(f"{loopVarFile} = os.path.join({loopVarRoot},{loopVarFile})", indent=indent + code_generator.DEFAULT_INDENT*2)]

            code_generator.expandCodeWithCondition(self.loop_body_port, sourceCodeLines, innerLoopConditionCode, indent + code_generator.DEFAULT_INDENT, preBodyLines=preBodyLines)

            # Loop completion code:
            code_generator.expandExecCode(self.loop_complete_port, sourceCodeLines, indent)
