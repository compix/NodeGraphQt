from VisualScripting.node_exec.base_nodes import defNode, defInlineNode
import subprocess
import os

WINDOWS_NODE_IDENTIFIER = "Windows"

@defNode("Select in Explorer", isExecutable=True, identifier=WINDOWS_NODE_IDENTIFIER)
def selectInExplorer(path):
    if os.path.exists(path):
        subprocess.Popen(f'explorer /select,"{os.path.normpath(path)}"')

@defNode("Open File", isExecutable=True, identifier=WINDOWS_NODE_IDENTIFIER)
def openFile(filePath):
    if os.path.exists(filePath):
        subprocess.Popen(f'explorer /start,"{os.path.normpath(filePath)}"')