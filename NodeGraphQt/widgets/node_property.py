#!/usr/bin/python
from NodeGraphQt import QtCore, QtWidgets

from NodeGraphQt.constants import Z_VAL_NODE_WIDGET
from NodeGraphQt.widgets.stylesheet import *


class _NodeGroupBox(QtWidgets.QGroupBox):

    def __init__(self, label, parent=None):
        super(_NodeGroupBox, self).__init__(parent)
        margin = (0, 5, 0, 0)
        padding_top = '14px'
        if label == '':
            margin = (0, 2, 0, 0)
            padding_top = '2px'
        style = STYLE_QGROUPBOX.replace('$PADDING_TOP', padding_top)
        self.setTitle(label)
        self.setStyleSheet(style)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(*margin)
        self._layout.setSpacing(1)
        self.setLayout(self._layout)

    def add_node_widget(self, widget):
        self._layout.addWidget(widget)

class NodeBaseWidget(QtWidgets.QWidget):
    """
    Base Node Widget.
    """

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None, name='widget', label=''):
        super().__init__(parent._nodeItemFrame._frame)
        self._name = name
        self._label = label

    def _value_changed(self):
        self.value_changed.emit(self.name, self.value)

    def setToolTip(self, tooltip):
        tooltip = tooltip.replace('\n', '<br/>')
        tooltip = '<b>{}</b><br/>{}'.format(self.name, tooltip)
        super(NodeBaseWidget, self).setToolTip(tooltip)

    def setWidget(self, widget):
        self._widget = widget

    @property
    def widget(self):
        raise NotImplementedError

    @property 
    def graphicsWidget(self):
        return self._widget

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, text):
        raise NotImplementedError

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def type_(self):
        return str(self.__class__.__name__)

    @property
    def node(self):
        self.parentItem()

    @property
    def name(self):
        return self._name

    @property
    def has_property(self):
        return True


class NodeComboBox(NodeBaseWidget):
    """
    ComboBox Node Widget.
    """

    def __init__(self, parent=None, name='', label='', items=None):
        super(NodeComboBox, self).__init__(parent, name, label)
        self._combo = QtWidgets.QComboBox()
        self._combo.setStyleSheet(STYLE_QCOMBOBOX)
        self._combo.setMinimumHeight(24)
        self._combo.setMinimumWidth(200)
        self._combo.currentIndexChanged.connect(self._value_changed)
        list_view = QtWidgets.QListView(self._combo)
        list_view.setStyleSheet(STYLE_QLISTVIEW)
        self._combo.setView(list_view)
        self._combo.clearFocus()
        self.add_items(items)
        group = _NodeGroupBox(label)
        group.add_node_widget(self._combo)
        group.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setWidget(group)

    @property
    def type_(self):
        return 'ComboNodeWidget'

    @property
    def widget(self):
        return self._combo

    @property
    def value(self):
        return str(self._combo.currentText())

    @value.setter
    def value(self, text=''):
        if text != self.value:
            index = self._combo.findText(text, QtCore.Qt.MatchExactly)
            self._combo.setCurrentIndex(index)

    def add_item(self, item):
        self._combo.addItem(item)

    def add_items(self, items=None):
        if items:
            self._combo.addItems(items)

    def all_items(self):
        return [self._combo.itemText(i) for i in range(self._combo.count)]

    def sort_items(self):
        items = sorted(self.all_items())
        self._combo.clear()
        self._combo.addItems(items)

    def clear(self):
        self._combo.clear()


class NodeLineEdit(NodeBaseWidget):
    """
    LineEdit Node Widget.
    """

    def __init__(self, parent=None, name='', label='', text=''):
        super(NodeLineEdit, self).__init__(parent, name, label)
        self._ledit = QtWidgets.QLineEdit()
        self._ledit.setStyleSheet(STYLE_QLINEEDIT)
        self._ledit.setAlignment(QtCore.Qt.AlignCenter)
        self._ledit.returnPressed.connect(self._value_changed)
        self._ledit.clearFocus()
        group = _NodeGroupBox(label)
        group.add_node_widget(self._ledit)
        group.setMinimumWidth(120)
        self.setWidget(group)
        self.text = text

    @property
    def type_(self):
        return 'LineEditNodeWidget'

    @property
    def widget(self):
        return self._ledit

    @property
    def value(self):
        return str(self._ledit.text())

    @value.setter
    def value(self, text=''):
        if text != self.value:
            self._ledit.setText(text)
            self._value_changed()


class NodeCheckBox(NodeBaseWidget):
    """
    CheckBox Node Widget.
    """

    def __init__(self, parent=None, name='', label='', text='', state=False):
        super(NodeCheckBox, self).__init__(parent, name, label)
        self._cbox = QtWidgets.QCheckBox(text)
        self._cbox.setChecked(state)
        self._cbox.setMinimumWidth(80)
        self._cbox.setStyleSheet(STYLE_QCHECKBOX)
        #self._cbox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        font = self._cbox.font()
        font.setPointSize(11)
        self._cbox.setFont(font)
        self._cbox.stateChanged.connect(self._value_changed)
        group = _NodeGroupBox(label)
        group.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        group.add_node_widget(self._cbox)
        self.setWidget(group)
        self.text = text
        self.state = state

    @property
    def type_(self):
        return 'CheckboxNodeWidget'

    @property
    def widget(self):
        return self._cbox

    @property
    def value(self):
        return self._cbox.isChecked()

    @value.setter
    def value(self, state=False):
        if state != self.value:
            self._cbox.setChecked(state)
