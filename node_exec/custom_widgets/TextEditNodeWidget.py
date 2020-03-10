from NodeGraphQt.widgets.node_property import NodeBaseWidget, _NodeGroupBox, Z_VAL_NODE_WIDGET, STYLE_QLINEEDIT
from NodeGraphQt.qgraphics.node_backdrop import BackdropSizer, NODE_SEL_BORDER_COLOR
from PySide2 import QtWidgets, QtCore, QtGui

class TextSizer(QtWidgets.QGraphicsItem):
    """
    Sizer item for resizing a backdrop item.

    Args:
        parent (BackdropNodeItem): the parent node item.
        size (float): sizer size.
    """

    def __init__(self, parent=None, controller=None, size=6.0):
        super().__init__(parent)
        self.setZValue(Z_VAL_NODE_WIDGET)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        self.setToolTip('double-click auto resize')
        self._size = size
        self.controller = controller

    @property
    def size(self):
        return self._size

    def set_pos(self, x, y):
        x -= self._size
        y -= self._size
        self.setPos(x, y)

    def boundingRect(self):
        return QtCore.QRectF(0.5, 0.5, self._size, self._size)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            item = self.parentItem()
            mx, my = self.controller.minimum_size
            x = mx if value.x() < mx else value.x()
            y = my if value.y() < my else value.y()
            value = QtCore.QPointF(x, y)
            self.controller.on_sizer_pos_changed(value)
            return value
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        item = self.parentItem()
        self.controller.on_sizer_double_clicked()

    def paint(self, painter, option, widget):
        """
        Draws the backdrop sizer on the bottom right corner.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()

        rect = self.boundingRect()
        item = self.parentItem()
        if item and item.selected:
            color = QtGui.QColor(*NODE_SEL_BORDER_COLOR)
        else:
            color = QtGui.QColor(*item.color)
            color = color.darker(110)
        path = QtGui.QPainterPath()
        path.moveTo(rect.topRight())
        path.lineTo(rect.bottomRight())
        path.lineTo(rect.bottomLeft())
        painter.setBrush(color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.fillPath(path, painter.brush())

        painter.restore()

class TextEditNodeWidget(NodeBaseWidget):
    """
    TextEdit Node Widget.
    """

    def __init__(self, parent=None, name='', label='', text=''):
        super().__init__(parent, name, label)

        self.viewer = None

        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setMinimumWidth(80)
        self.textEdit.setMinimumHeight(80)
        self.textEdit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.textEdit.setAlignment(QtCore.Qt.AlignTop)
        self.textEdit.textChanged.connect(self._value_changed)
        self.textEdit.clearFocus()
        self.group = _NodeGroupBox(label)
        self.group.add_node_widget(self.textEdit)
        self.group.setAlignment(QtCore.Qt.AlignTop)
        self.group._layout.setAlignment(QtCore.Qt.AlignTop)
        self.group.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setWidget(self.group)
        self.text = text
        self.parent = parent
        self.minSize = (80,80)

        self.sizer = TextSizer(self.parent, self, 20.0)
        self.parent.pre_init = self.pre_init

    def on_sizer_pos_changed(self, pos):
        bg_margin = 1

        prevWidth = self.parent._width
        prevHeight = self.parent._height
        self.parent._width = pos.x() + self.sizer.size + bg_margin
        self.parent._height = pos.y() + self.sizer.size + bg_margin

        dw = self.parent._width - prevWidth
        dh = self.parent._height - prevHeight

        self.group.setFixedSize(self.group.width() + dw, self.group.height() + dh)

        self.parent.draw_node()

    def pre_init(self, viewer, pos=None):
        w,h = self.parent.calc_size()
        self.viewer = viewer

        self.minSize = (w, h)
        self.sizer.set_pos(0,0)
        self.on_sizer_pos_changed(self.sizer.pos())

    @property
    def minimum_size(self):
        return self.minSize

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