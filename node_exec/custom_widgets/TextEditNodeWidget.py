from NodeGraphQt.widgets.node_property import NodeBaseWidget, _NodeGroupBox, Z_VAL_NODE_WIDGET, STYLE_QLINEEDIT
from NodeGraphQt.qgraphics.node_backdrop import BackdropSizer, NODE_SEL_BORDER_COLOR
from NodeGraphQt.qgraphics.node_base import NodeItem
from PySide2 import QtWidgets, QtCore, QtGui

class TextEditNodeWidget(NodeBaseWidget):
    """
    TextEdit Node Widget.
    """

    def __init__(self, parent=None, name='', label='', text=''):
        super().__init__(parent, name, label)

        self.viewer = None

        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.textEdit.setAlignment(QtCore.Qt.AlignTop)
        self.textEdit.textChanged.connect(self._value_changed)
        self.textEdit.clearFocus()
        self.textEdit.setMinimumSize(80,17)
        self.group = _NodeGroupBox(label)
        self.group.add_node_widget(self.textEdit)
        self.group.setAlignment(QtCore.Qt.AlignTop)
        self.group._layout.setAlignment(QtCore.Qt.AlignTop)
        self.group.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setWidget(self.group)
        self.text = text
        self.parent : NodeItem = parent
        
        self.parent.setResizable(True)

    @property
    def type_(self):
        return 'LineEditNodeWidget'

    @property
    def widget(self):
        return self.textEdit

    @property
    def value(self):
        return str(self.textEdit.toPlainText())

    @value.setter
    def value(self, text=''):
        if text != self.value:
            self.textEdit.setText(text)
            self._value_changed()