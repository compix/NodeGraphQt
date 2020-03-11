from node_exec.base_nodes import defNode, defInlineNode, BaseCustomNode
from PySide2.QtWidgets import QFileDialog

IDENTIFIER = 'File Dialog'

@defNode("Choose Existing Directory", isExecutable=True, returnNames=["directory"], identifier=IDENTIFIER)
def chooseExistingDirectory(parentWindow=None, initialDir=""):
    return QFileDialog.getExistingDirectory(parentWindow, "Open Directory", initialDir)

@defNode("Choose File Name", isExecutable=True, returnNames=["filename", "selectedFilter"], identifier=IDENTIFIER)
def chooseFileName(parentWindow=None, initialDir="", extensionFilter="Example (*.example *.exml);;Images (*.jpg *.tif)", selectedFilter=""):
    return QFileDialog.getOpenFileName(parentWindow, "Open File", initialDir, extensionFilter)

@defNode("Choose File Names", isExecutable=True, returnNames=["filenames", "selectedFilter"], identifier=IDENTIFIER)
def chooseFileNames(parentWindow=None, initialDir="", extensionFilter="Example (*.example *.exml);;Images (*.jpg *.tif)", selectedFilter=""):
    return QFileDialog.getOpenFileNames(parentWindow, "Open Files", initialDir, extensionFilter)

@defNode("Choose Save File Name", isExecutable=True, returnNames=["filename", "selectedFilter"], identifier=IDENTIFIER)
def chooseSaveFileName(parentWindow=None, initialDir="", extensionFilter="Example (*.example *.exml);;Jpegs (*.jpg);;Tiffs (*.tif)", selectedFilter=""):
    return QFileDialog.getSaveFileName(parentWindow, "Save File", initialDir, extensionFilter)
