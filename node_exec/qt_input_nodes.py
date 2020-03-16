from node_exec.base_nodes import defNode
from PySide2.QtWidgets import QInputDialog, QLineEdit

IDENTIFIER = 'Input Dialog'

@defNode("Choose Item", isExecutable=True, returnNames=["item", "accepted"], identifier=IDENTIFIER)
def getItem(parentWindow=None, title="Item Selection", label="Item:", items=["t0", "t1"], current=0, editable=True):
    return QInputDialog.getItem(parentWindow, title, label, items, current, editable)

@defNode("Double Input", isExecutable=True, returnNames=["double", "accepted"], identifier=IDENTIFIER)
def getDouble(parentWindow=None, title="Double Input", label="Double:", value=0, minValue=-2147483647, maxValue=2147483647, decimals=1):
    return QInputDialog.getDouble(parentWindow, title, label, value, minValue, maxValue, decimals)

@defNode("Integer Input", isExecutable=True, returnNames=["integer", "accepted"], identifier=IDENTIFIER)
def getInt(parentWindow=None, title="Integer Input", label="Integer:", value=0, minValue=-2147483647, maxValue=2147483647, step=1):
    return QInputDialog.getInt(parentWindow, title, label, value, minValue, maxValue, step)

@defNode("Text Input", isExecutable=True, returnNames=["text", "accepted"], identifier=IDENTIFIER)
def getText(parentWindow=None, title="Text Input", label="Text:", text=""):
    return QInputDialog.getText(parentWindow, title, label, QLineEdit.Normal, text)

@defNode("MultiLine Text Input", isExecutable=True, returnNames=["text", "accepted"], identifier=IDENTIFIER)
def getMultiLineText(parentWindow=None, title="Text Input", label="Text:", text=""):
    return QInputDialog.getMultiLineText(parentWindow, title, label, text)