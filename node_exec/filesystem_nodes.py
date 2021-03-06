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

@defNode("Path Exists", returnNames=["exists"], identifier=IDENTIFIER)
def pathExists(path):
    return os.path.exists(path)

@defNode("Is File", returnNames=["isFile"], identifier=IDENTIFIER)
def isFile(path):
    return os.path.isfile(path)

@defNode("Is Directory", returnNames=["isDir"], identifier=IDENTIFIER)
def isDirectory(path):
    return os.path.isdir(path)

@defNode("Path Basename", returnNames=["basename"], identifier=IDENTIFIER)
def getPathBasename(path):
    return os.path.basename(path)

@defNode("Path Directory", returnNames=["name"], identifier=IDENTIFIER)
def getPathDirName(path):
    return os.path.dirname(path)

@defNode("File Extension", returnNames=["ext"], identifier=IDENTIFIER)
def getFileExtension(filePath):
    return os.path.splitext(filePath)[1]

@defNode("Path Basename Without Extension", returnNames=["name"], identifier=IDENTIFIER)
def getPathBasenameWithoutExt(filePath):
    return os.path.splitext(os.path.basename(filePath))[0]

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
            self.recursiveInput = self.add_input('recursive', default_value=True)

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

            sourceCodeLines.append(code_generator.makeCodeLine(f"if not {code_generator.getParamName(self.recursiveInput)}:", indent=indent + code_generator.DEFAULT_INDENT))
            sourceCodeLines.append(code_generator.makeCodeLine(f"break", indent=indent + code_generator.DEFAULT_INDENT*2))

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
            self.add_output('basename')
            self.add_output('basenameWithoutExtension')
            self.add_output('extension')
            self.dirInput = self.add_input('directory')

            self.extensionsInput = self.add_input('extensions', default_value=None)
            self.recursiveInput = self.add_input('recursive', default_value=True)

        @property
        def importLines(self):
            return ["import os"]

        def generateCode(self, sourceCodeLines, indent):
            directory = code_generator.getParamName(self.dirInput)
            extensions = code_generator.getParamName(self.extensionsInput)

            # Loop body code:
            loopVarFile = code_generator.getVarNameSource(self, idx=0)
            basenameOut = code_generator.getVarNameSource(self, idx=1)
            basenameWithoutExtensionOut = code_generator.getVarNameSource(self, idx=2)
            extensionOut = code_generator.getVarNameSource(self, idx=3)

            loopVarRoot = code_generator.getVarNameSource(self, idx=4)
            loopVarFiles = code_generator.getVarNameSource(self, idx=5)

            walkStatement = f"os.walk({directory})"
            loopConditionCode = code_generator.makeCodeLine(f"for {loopVarRoot},_,{loopVarFiles} in {walkStatement}:", indent)
            sourceCodeLines.append(loopConditionCode)
            innerLoopConditionCode = code_generator.makeCodeLine(f"for {loopVarFile} in {loopVarFiles}:", indent + code_generator.DEFAULT_INDENT)
            preBodyLines = [code_generator.makeCodeLine(f"{loopVarFile} = os.path.join({loopVarRoot},{loopVarFile})", indent=indent + code_generator.DEFAULT_INDENT*2),
                            code_generator.makeCodeLine(f"{basenameOut} = os.path.basename({loopVarFile})", indent=indent + code_generator.DEFAULT_INDENT*2),
                            code_generator.makeCodeLine(f"{basenameWithoutExtensionOut} = os.path.splitext(os.path.basename({loopVarFile}))[0]", indent=indent + code_generator.DEFAULT_INDENT*2),
                            code_generator.makeCodeLine(f"{extensionOut} = os.path.splitext({loopVarFile})[1]", indent=indent + code_generator.DEFAULT_INDENT*2),
                            code_generator.makeCodeLine(f"if {extensions} != None and not {extensionOut} in {extensions}:", indent=indent + code_generator.DEFAULT_INDENT*2),
                            code_generator.makeCodeLine(f"continue", indent=indent + code_generator.DEFAULT_INDENT*3)]

            code_generator.expandCodeWithCondition(self.loop_body_port, sourceCodeLines, innerLoopConditionCode, indent + code_generator.DEFAULT_INDENT, preBodyLines=preBodyLines)

            sourceCodeLines.append(code_generator.makeCodeLine(f"if not {code_generator.getParamName(self.recursiveInput)}:", indent=indent + code_generator.DEFAULT_INDENT))
            sourceCodeLines.append(code_generator.makeCodeLine(f"break", indent=indent + code_generator.DEFAULT_INDENT*2))

            # Loop completion code:
            code_generator.expandExecCode(self.loop_complete_port, sourceCodeLines, indent)
