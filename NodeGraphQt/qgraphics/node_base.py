#!/usr/bin/python

from NodeGraphQt import QtGui, QtCore, QtWidgets
from NodeGraphQt.constants import (IN_PORT, OUT_PORT,
                                   NODE_WIDTH, NODE_HEIGHT,
                                   NODE_ICON_SIZE, ICON_NODE_BASE,
                                   NODE_SEL_COLOR, NODE_SEL_BORDER_COLOR,
                                   PORT_FALLOFF, Z_VAL_NODE, Z_VAL_NODE_WIDGET, 
                                   PORT_SPACING, NODE_TOP_BORDER_HEIGHT)
from NodeGraphQt.errors import NodeWidgetError
from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem
from NodeGraphQt.qgraphics.port import PortItem

class NodeItemSizer(QtWidgets.QGraphicsItem):
    """
    Sizer item for resizing a NodeItem.
    """
    def __init__(self, parent, controller = None, size=6.0):
        self._size = size

        super().__init__(parent)
        self.setZValue(Z_VAL_NODE_WIDGET)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        self.setToolTip('double-click auto resize')
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
            mx, my = self.controller.minimum_size
            x = mx if value.x() < mx else value.x()
            y = my if value.y() < my else value.y()
            value = QtCore.QPointF(x, y)
            self.controller.on_sizer_pos_changed(value)
            return value
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        self.controller.on_sizer_double_clicked()

    def paint(self, painter, option, widget):
        """
        Draws the sizer on the bottom right corner.

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
            color = color.darker(50)
        path = QtGui.QPainterPath()
        path.moveTo(rect.topRight())
        path.lineTo(rect.bottomRight())
        path.lineTo(rect.bottomLeft())
        painter.setBrush(color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.fillPath(path, painter.brush())

        painter.restore()

    def delete(self):
        self.scene().removeItem(self)

class XDisabledItem(QtWidgets.QGraphicsItem):
    """
    Node disabled overlay item.

    Args:
        parent (NodeItem): the parent node item.
        text (str): disable overlay text.
    """

    def __init__(self, parent=None, text=None):
        super(XDisabledItem, self).__init__(parent)
        self.setZValue(Z_VAL_NODE_WIDGET + 2)
        self.setVisible(False)
        self.color = (0, 0, 0, 255)
        self.text = text

    def boundingRect(self):
        return self.parentItem().boundingRect()

    def paint(self, painter, option, widget):
        """
        Draws the overlay disabled X item on top of a node item.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()

        margin = 20
        rect = self.boundingRect()
        dis_rect = QtCore.QRectF(rect.left() - (margin / 2),
                                 rect.top() - (margin / 2),
                                 rect.width() + margin,
                                 rect.height() + margin)
        pen = QtGui.QPen(QtGui.QColor(*self.color), 8)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(dis_rect.topLeft(), dis_rect.bottomRight())
        painter.drawLine(dis_rect.topRight(), dis_rect.bottomLeft())

        bg_color = QtGui.QColor(*self.color)
        bg_color.setAlpha(100)
        bg_margin = -0.5
        bg_rect = QtCore.QRectF(dis_rect.left() - (bg_margin / 2),
                                dis_rect.top() - (bg_margin / 2),
                                dis_rect.width() + bg_margin,
                                dis_rect.height() + bg_margin)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        painter.setBrush(bg_color)
        painter.drawRoundedRect(bg_rect, 5, 5)

        pen = QtGui.QPen(QtGui.QColor(155, 0, 0, 255), 0.7)
        painter.setPen(pen)
        painter.drawLine(dis_rect.topLeft(), dis_rect.bottomRight())
        painter.drawLine(dis_rect.topRight(), dis_rect.bottomLeft())

        point_size = 4.0
        point_pos = (dis_rect.topLeft(), dis_rect.topRight(),
                     dis_rect.bottomLeft(), dis_rect.bottomRight())
        painter.setBrush(QtGui.QColor(255, 0, 0, 255))
        for p in point_pos:
            p.setX(p.x() - (point_size / 2))
            p.setY(p.y() - (point_size / 2))
            point_rect = QtCore.QRectF(
                p, QtCore.QSizeF(point_size, point_size))
            painter.drawEllipse(point_rect)

        if self.text:
            font = painter.font()
            font.setPointSize(10)

            painter.setFont(font)
            font_metrics = QtGui.QFontMetrics(font)
            font_width = font_metrics.width(self.text)
            font_height = font_metrics.height()
            txt_w = font_width * 1.25
            txt_h = font_height * 2.25
            text_bg_rect = QtCore.QRectF((rect.width() / 2) - (txt_w / 2),
                                         (rect.height() / 2) - (txt_h / 2),
                                         txt_w, txt_h)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 0.5))
            painter.setBrush(QtGui.QColor(*self.color))
            painter.drawRoundedRect(text_bg_rect, 2, 2)

            text_rect = QtCore.QRectF((rect.width() / 2) - (font_width / 2),
                                      (rect.height() / 2) - (font_height / 2),
                                      txt_w * 2, font_height * 2)

            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 1))
            painter.drawText(text_rect, self.text)

        painter.restore()

class NodeItemFrame(QtWidgets.QGraphicsProxyWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parentNodeItem = parent
        self.resizeEventListener = None
        self.setZValue(Z_VAL_NODE_WIDGET)

        self._frame = QtWidgets.QFrame()
        self._frame.setObjectName("_mainNodeFrame")
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setSpacing(1)
        self._frame.setLayout(self._layout)
        self._frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._frame.setStyleSheet("QFrame#_mainNodeFrame { background-color:transparent; }")

        self.setWidget(self._frame)

    @property
    def layout(self):
        return self._layout

    @property
    def frame(self):
        return self._frame

    @property
    def width(self):
        return self._frame.width()

    @property
    def height(self):
        return self._frame.height()

    @property
    def minWidth(self):
        return self._frame.minimumSizeHint().width()

    @property
    def minHeight(self):
        return self._frame.minimumSizeHint().height()

    def resizeEvent(self, evt):
        if self.resizeEventListener:
            self.resizeEventListener.onFrameResize(self.width, self.height)

    def registerResizeEvent(self, listener):
        self.resizeEventListener = listener

class NodeItem(AbstractNodeItem):
    """
    Base Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='node', parent=None):
        super(NodeItem, self).__init__(name, parent)
        pixmap = QtGui.QPixmap(ICON_NODE_BASE)
        if pixmap.size().height() > NODE_ICON_SIZE:
            pixmap = pixmap.scaledToHeight(NODE_ICON_SIZE,
                                           QtCore.Qt.SmoothTransformation)
        self._properties['icon'] = ICON_NODE_BASE
        self._icon_item = QtWidgets.QGraphicsPixmapItem(pixmap, self)
        self._icon_item.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self._text_item = QtWidgets.QGraphicsTextItem(self.name, self)
        self._x_item = XDisabledItem(self, 'DISABLED')
        self._input_items = {}
        self._output_items = {}
        self._widgets = {}

        self._nodeItemFrame = NodeItemFrame(self)
        self._layout = self._nodeItemFrame.layout
        self._nodeItemFrame.registerResizeEvent(self)

        self.sizer : NodeItemSizer = None
        self.sizerSize = 20.0

    def paint(self, painter, option, widget):
        """
        Draws the node base not the ports.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()
        bg_border = 1.0
        rect = QtCore.QRectF(0.5 - (bg_border / 2),
                             0.5 - (bg_border / 2),
                             self._width + bg_border,
                             self._height + bg_border)
        radius = 2
        border_color = QtGui.QColor(*self.border_color)

        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        rect = self.boundingRect()
        bg_color = QtGui.QColor(*self.color)
        painter.setBrush(bg_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        if self.selected and NODE_SEL_COLOR:
            painter.setBrush(QtGui.QColor(*NODE_SEL_COLOR))
            painter.drawRoundedRect(rect, radius, radius)

        label_rect = QtCore.QRectF(rect.left() + (radius / 2),
                                   rect.top() + (radius / 2),
                                   self._width - (radius / 1.25),
                                   NODE_TOP_BORDER_HEIGHT)
        path = QtGui.QPainterPath()
        path.addRoundedRect(label_rect, radius / 1.5, radius / 1.5)
        painter.setBrush(QtGui.QColor(0, 0, 0, 50))
        painter.fillPath(path, painter.brush())

        border_width = 0.8
        if self.selected and NODE_SEL_BORDER_COLOR:
            border_width = 1.2
            border_color = QtGui.QColor(*NODE_SEL_BORDER_COLOR)
        border_rect = QtCore.QRectF(rect.left() - (border_width / 2),
                                    rect.top() - (border_width / 2),
                                    rect.width() + border_width,
                                    rect.height() + border_width)

        pen = QtGui.QPen(border_color, border_width)
        pen.setCosmetic(self.viewer() != None and self.viewer().get_zoom() < 0.0)
        path = QtGui.QPainterPath()
        path.addRoundedRect(border_rect, radius, radius)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawPath(path)

        painter.restore()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            start = PortItem().boundingRect().width() - PORT_FALLOFF
            end = self.boundingRect().width() - start
            x_pos = event.pos().x()
            if not start <= x_pos <= end:
                event.ignore()
        super(NodeItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.modifiers() == QtCore.Qt.AltModifier:
            event.ignore()
            return
        super(NodeItem, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        viewer = self.viewer()
        if viewer:
            viewer.node_double_clicked.emit(self.id)
        super(NodeItem, self).mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        if change == self.ItemSelectedChange and self.scene():
            self.reset_pipes()
            if value:
                self.hightlight_pipes()
            self.setZValue(Z_VAL_NODE)
            if not self.selected:
                self.setZValue(Z_VAL_NODE + 1)

        return super(NodeItem, self).itemChange(change, value)

    def _tooltip_disable(self, state):
        tooltip = '<b>{}</b>'.format(self.name)
        if state:
            tooltip += ' <font color="red"><b>(DISABLED)</b></font>'
        tooltip += '<br/>{}<br/>'.format(self.type_)
        self.setToolTip(tooltip)

    def _set_base_size(self, add_w=0.0, add_h=0.0):
        """
        setup initial base size.

        Args:
            add_w (float): additional width.
            add_h (float): additional height.
        """
        self._width = max(self._width, NODE_WIDTH)
        self._height = max(self._height, NODE_HEIGHT)
        width, height = self.calc_size(add_w, add_h)
        if width > self._width:
            self._width = width
        if height > self._height:
            self._height = height

        if self.sizer:
            frameWidth, frameHeight = self.determine_frame_size()
            self.setFrameSize(max(frameWidth, self._nodeItemFrame.minWidth), max(frameHeight, self._nodeItemFrame.minHeight))

    def _set_text_color(self, color):
        """
        set text color.

        Args:
            color (tuple): color value in (r, g, b, a).
        """
        text_color = QtGui.QColor(*color)
        for port, text in self._input_items.items():
            text.setDefaultTextColor(text_color)
        for port, text in self._output_items.items():
            text.setDefaultTextColor(text_color)
        self._text_item.setDefaultTextColor(text_color)

    def activate_pipes(self):
        """
        active pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.activate()

    def hightlight_pipes(self):
        """
        highlight pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.highlight()

    def reset_pipes(self):
        """
        reset the pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.reset()

    def calc_in_port_size(self):
        port_height = 0.0
        port_width = 0.0
        input_widths = []
        if self._input_items:
            for port, text in self._input_items.items():
                if port.isVisible():
                    input_width = port.boundingRect().width() - PORT_FALLOFF
                    if text.isVisible():
                        input_width += text.boundingRect().width() / 1.5
                    input_widths.append(input_width)
                    port_height += port.boundingRect().height()

            port_width = max(input_widths)
        
        port_height += (max(len(input_widths), 1) - 1) * PORT_SPACING

        return port_width, port_height

    def calc_out_port_size(self):
        port_height = 0.0
        port_width = 0.0
        output_widths = []
        if self._output_items:
            for port, text in self._output_items.items():
                if port.isVisible():
                    output_width = port.boundingRect().width()
                    if text.isVisible():
                        output_width += text.boundingRect().width() / 1.5
                    output_widths.append(output_width)
                    port_height += port.boundingRect().height()

            port_width = max(output_widths)

        port_height += (max(len(output_widths), 1) - 1) * PORT_SPACING

        return port_width, port_height

    def calc_size(self, add_w=0.0, add_h=0.0, minSize=False):
        """
        calculate minimum node size.

        Args:
            add_w (float): additional width.
            add_h (float): additional height.
        """
        width = self._text_item.boundingRect().width()
        height = self._text_item.boundingRect().height()

        portInWidth, portInHeight = self.calc_in_port_size()
        portOutWidth, portOutHeight = self.calc_out_port_size()

        height += max(portInHeight, portOutHeight)

        if self._widgets:
            wid_width = self._nodeItemFrame.minWidth if minSize else self._nodeItemFrame.width
            width = max(width, wid_width)

        width += portInWidth + portOutWidth

        if self._widgets:
            wid_height = self._nodeItemFrame.minHeight if minSize else self._nodeItemFrame.height
            height = max(wid_height, height)

        width += add_w
        height += add_h

        if self.sizer:
            width += self.sizerSize
            height += self.sizerSize

        return width, height

    def determine_frame_size(self):
        """
        Determine the frame size from the current _width and _height.
        """
        height = self._height - NODE_TOP_BORDER_HEIGHT
        inW,_ = self.calc_in_port_size()
        outW,_ = self.calc_out_port_size()
        width = self._width - inW - outW

        if self.sizer:
            width -= self.sizerSize
            height -= self.sizerSize

        return width, height

    def arrange_icon(self, h_offset=0.0, v_offset=0.0):
        """
        Arrange node icon to the default top left of the node.

        Args:
            v_offset (float): vertical offset.
            h_offset (float): horizontal offset.
        """
        x = 2.0 + h_offset
        y = 2.0 + v_offset
        self._icon_item.setPos(x, y)

    def arrange_label(self, h_offset=0.0, v_offset=0.0):
        """
        Arrange node label to the default top center of the node.

        Args:
            v_offset (float): vertical offset.
            h_offset (float): horizontal offset.
        """
        text_rect = self._text_item.boundingRect()
        text_x = (self._width / 2) - (text_rect.width() / 2)
        text_x += h_offset
        text_y = 1.0 + v_offset
        self._text_item.setPos(text_x, text_y)

    def arrange_widgets(self, v_offset=0.0):
        """
        Arrange node widgets to the default center of the node.

        Args:
            v_offset (float): vertical offset.
        """

        frameWidth = self._nodeItemFrame.width
        frameHeight = self._nodeItemFrame.height
        xPos = self._width * 0.5 - frameWidth * 0.5
        yPos = self._height * 0.5 - frameHeight * 0.5 + v_offset
        self._nodeItemFrame.setPos(xPos, yPos)

    def arrange_ports(self, v_offset=0.0):
        """
        Arrange input, output ports in the node layout.
    
        Args:
            v_offset (float): port vertical offset.
        """
        width = self._width
        txt_offset = PORT_FALLOFF - 2
        spacing = PORT_SPACING

        # adjust input position
        inputs = [p for p in self.inputs if p.isVisible()]
        if inputs:
            port_width = inputs[0].boundingRect().width()
            port_height = inputs[0].boundingRect().height()
            port_x = (port_width / 2) * -1
            port_y = v_offset
            for port in inputs:
                port.setPos(port_x, port_y)
                port_y += port_height + spacing
        # adjust input text position
        for port, text in self._input_items.items():
            if port.isVisible():
                txt_x = port.boundingRect().width() / 2 - txt_offset
                text.setPos(txt_x, port.y() - 1.5)

        # adjust output position
        outputs = [p for p in self.outputs if p.isVisible()]
        if outputs:
            port_width = outputs[0].boundingRect().width()
            port_height = outputs[0].boundingRect().height()
            port_x = width - (port_width / 2)
            port_y = v_offset
            for port in outputs:
                port.setPos(port_x, port_y)
                port_y += port_height + spacing
        # adjust output text position
        for port, text in self._output_items.items():
            if port.isVisible():
                txt_width = text.boundingRect().width() - txt_offset
                txt_x = port.x() - txt_width
                text.setPos(txt_x, port.y() - 1.5)

    def offset_label(self, x=0.0, y=0.0):
        """
        offset the label in the node layout.

        Args:
            x (float): horizontal x offset
            y (float): vertical y offset
        """
        icon_x = self._text_item.pos().x() + x
        icon_y = self._text_item.pos().y() + y
        self._text_item.setPos(icon_x, icon_y)

    def draw_node(self):
        """
        Draw the node item in the scene.
        """
        height = NODE_TOP_BORDER_HEIGHT

        # setup initial base size.
        self._set_base_size(add_w=0.0, add_h=height)
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- setup node layout ---

        # arrange label text
        self.arrange_label(h_offset=0.0, v_offset=0.0)
        # arrange icon
        self.arrange_icon(h_offset=0.0, v_offset=0.0)
        # arrange input and output ports.
        self.arrange_ports(v_offset=height + (height / 2))
        # arrange node widgets
        self.arrange_widgets(v_offset=height / 2)

    def post_init(self, viewer=None, pos=None):
        """
        Called after node has been added into the scene.
        Adjust the node layout and form after the node has been added.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): not used
            pos (tuple): cursor position.
        """
        if self.sizer:
            self.initResizable()
        else:
            self.draw_node()

        # set initial node position.
        if pos:
            self.xy_pos = pos

    @property
    def icon(self):
        return self._properties['icon']

    @icon.setter
    def icon(self, path=None):
        self._properties['icon'] = path
        path = path or ICON_NODE_BASE
        pixmap = QtGui.QPixmap(path)
        if pixmap.size().height() > NODE_ICON_SIZE:
            pixmap = pixmap.scaledToHeight(NODE_ICON_SIZE,
                                           QtCore.Qt.SmoothTransformation)
        self._icon_item.setPixmap(pixmap)
        if self.scene():
            self.post_init()

    @AbstractNodeItem.width.setter
    def width(self, width=0.0):
        w, h = self.calc_size()
        width = width if width > w else w
        AbstractNodeItem.width.fset(self, width)

    @AbstractNodeItem.height.setter
    def height(self, height=0.0):
        w, h = self.calc_size()
        h = 70 if h < 70 else h
        height = height if height > h else h
        AbstractNodeItem.height.fset(self, height)

    @AbstractNodeItem.disabled.setter
    def disabled(self, state=False):
        AbstractNodeItem.disabled.fset(self, state)
        for n, w in self._widgets.items():
            w.widget.setDisabled(state)
        self._tooltip_disable(state)
        self._x_item.setVisible(state)

    @AbstractNodeItem.selected.setter
    def selected(self, selected=False):
        AbstractNodeItem.selected.fset(self, selected)
        if selected:
            self.hightlight_pipes()

    @AbstractNodeItem.name.setter
    def name(self, name=''):
        AbstractNodeItem.name.fset(self, name)
        self._text_item.setPlainText(name)
        if self.scene():
            self.draw_node()

    @AbstractNodeItem.color.setter
    def color(self, color=(100, 100, 100, 255)):
        AbstractNodeItem.color.fset(self, color)
        if self.scene():
            self.scene().update()

    @AbstractNodeItem.text_color.setter
    def text_color(self, color=(100, 100, 100, 255)):
        AbstractNodeItem.text_color.fset(self, color)
        self._set_text_color(color)

    @property
    def inputs(self):
        """
        Returns:
            list[PortItem]: input port graphic items.
        """
        return list(self._input_items.keys())

    @property
    def outputs(self):
        """
        Returns:
            list[PortItem]: output port graphic items.
        """
        return list(self._output_items.keys())

    def add_input(self, name='input', multi_port=False, display_name=True):
        """
        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): display the port name. 

        Returns:
            PortItem: input item widget
        """
        port = PortItem(self)
        port.name = name
        port.port_type = IN_PORT
        port.multi_connection = multi_port
        port.display_name = display_name
        text = QtWidgets.QGraphicsTextItem(port.name, self)
        text.font().setPointSize(8)
        text.setFont(text.font())
        text.setVisible(display_name)
        self._input_items[port] = text
        if self.scene():
            self.post_init()
        return port

    def add_output(self, name='output', multi_port=False, display_name=True):
        """
        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): display the port name.

        Returns:
            PortItem: output item widget
        """
        port = PortItem(self)
        port.name = name
        port.port_type = OUT_PORT
        port.multi_connection = multi_port
        port.display_name = display_name
        text = QtWidgets.QGraphicsTextItem(port.name, self)
        text.font().setPointSize(8)
        text.setFont(text.font())
        text.setVisible(display_name)
        self._output_items[port] = text
        if self.scene():
            self.post_init()
        return port

    def get_input_text_item(self, port_item):
        """
        Args:
            port_item (PortItem): port item.

        Returns:
            QGraphicsTextItem: graphic item used for the port text.
        """
        return self._input_items[port_item]

    def get_output_text_item(self, port_item):
        """
        Args:
            port_item (PortItem): port item.

        Returns:
            QGraphicsTextItem: graphic item used for the port text.
        """
        return self._output_items[port_item]

    @property
    def widgets(self):
        return self._widgets.copy()

    def add_widget(self, widget):
        self._widgets[widget.name] = widget
        self._layout.addWidget(widget.graphicsWidget)

    def get_widget(self, name):
        widget = self._widgets.get(name)
        if widget:
            return widget
        raise NodeWidgetError('node has no widget "{}"'.format(name))

    def delete(self):
        for port, text in self._input_items.items():
            port.delete()
        for port, text in self._output_items.items():
            port.delete()
        super(NodeItem, self).delete()

    def from_dict(self, node_dict):
        super(NodeItem, self).from_dict(node_dict)
        widgets = node_dict.pop('widgets', {})
        for name, value in widgets.items():
            if self._widgets.get(name):
                self._widgets[name].value = value

    # Sizing:
    def setFrameSize(self, width, height):
        self._nodeItemFrame.frame.setFixedSize(width, height)

    def onFrameResize(self, width, height):
        self.draw_node()

    def setResizable(self, resizable):
        if (self.sizer != None) == resizable:
            return

        if resizable:
            self.sizer = NodeItemSizer(self, self, self.sizerSize)
        else:
            self.sizer.delete()
            self.sizer = None

    def initResizable(self):
        if self.sizer:
            minW, minH = self.minimum_size
            self._width, self._height = max(self._width, minW), max(self._height, minH)
            self.draw_node()
            QtCore.QCoreApplication.processEvents()
            self.sizer.set_pos(self._width,self._height)
            self.on_sizer_pos_changed(self.sizer.pos())

    def minimizeResizable(self):
        if self.sizer:
            self._width, self._height = self.minimum_size
            self.setFrameSize(self._nodeItemFrame.minWidth, self._nodeItemFrame.minHeight)
            QtCore.QCoreApplication.processEvents()
            self.draw_node()
            self.sizer.set_pos(self._width,self._height)
            self.on_sizer_pos_changed(self.sizer.pos())

    def adjustSize(self):
        self._width, self._height = self.calc_size(add_h=NODE_TOP_BORDER_HEIGHT * 0.5)
        self.draw_node()
        
    def pre_init(self, viewer, pos=None):
        super().pre_init(viewer, pos)

    def on_sizer_pos_changed(self, pos):
        prevWidth = self._width
        prevHeight = self._height
        self._width = pos.x() + self.sizer.size
        self._height = pos.y() + self.sizer.size

        dw = self._width - prevWidth
        dh = self._height - prevHeight

        frame = self._nodeItemFrame.frame
        self.setFrameSize(frame.width() + dw, frame.height() + dh)

        self.draw_node()

    def on_sizer_double_clicked(self):
        self.minimizeResizable()

    @property
    def minimum_size(self):
        minW, minH = self.calc_size(add_h=NODE_TOP_BORDER_HEIGHT * 0.5, minSize=True)
        return [minW, minH]