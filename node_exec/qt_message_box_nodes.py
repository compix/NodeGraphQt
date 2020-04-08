from node_exec.base_nodes import defNode
from PySide2.QtWidgets import QMessageBox

IDENTIFIER = "Message Box"

@defNode("Question Message Box", isExecutable=True, returnNames=["Clicked Yes"], identifier=IDENTIFIER)
def question(parentWindow=None, title="Question", text=""):
    return QMessageBox.question(parentWindow, title,text) == QMessageBox.Yes

@defNode("Critical Message Box", isExecutable=True, returnNames=["Clicked Ok"], identifier=IDENTIFIER)
def critical(parentWindow=None, title="Critical", text=""):
    return QMessageBox.critical(parentWindow, title, text) == QMessageBox.Ok

@defNode("Warning Message Box", isExecutable=True, returnNames=["Clicked Ok"], identifier=IDENTIFIER)
def warning(parentWindow=None, title="Warning", text=""):
    return QMessageBox.warning(parentWindow, title, text) == QMessageBox.Ok

@defNode("Information Message Box", isExecutable=True, returnNames=["Clicked Ok"], identifier=IDENTIFIER)
def information(parentWindow=None, title="Information", text=""):
    return QMessageBox.information(parentWindow, title, text) == QMessageBox.Ok

@defNode("About Message Box", isExecutable=True, returnNames=[], identifier=IDENTIFIER)
def about(parentWindow=None, title="About", text=""):
    QMessageBox.about(parentWindow, title, text)