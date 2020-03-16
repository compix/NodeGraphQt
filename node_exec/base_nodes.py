from NodeGraphQt.base.port import Port
from NodeGraphQt import BaseNode
from NodeGraphQt.base import node
from NodeGraphQt.constants import NODE_PROP_QLINEEDIT
from NodeGraphQt import QtWidgets
from NodeGraphQt.widgets.node_property import _NodeGroupBox, NodeBaseWidget
from NodeGraphQt.constants import IN_PORT, OUT_PORT
import node_exec.nodes_cfg
from node_exec.custom_widgets.TextEditNodeWidget import TextEditNodeWidget

DEFAULT_PORT_COLOR = (0,128,0)
EXECUTE_PORT_COLOR = (0,0,0)


DEFAULT_IDENTIFIER = 'Default'
PROPERTY_PREFIX = "p_"

def excludeFromRegistration(cls):
    node_exec.nodes_cfg.NODES_TO_REGISTER.remove(cls)
    return cls

def is_float(string):
    try:
        float(string)
        return True
    except:
        return False

def is_int(string):
    try:
        int(string)
        return True
    except:
        return False

class BaseCustomNode(BaseNode):
    __identifier__ = DEFAULT_IDENTIFIER
    NODE_NAME = 'BaseCustomNode'
    
    def __init_subclass__(cls, scm_type=None, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        node_exec.nodes_cfg.NODES_TO_REGISTER.append(cls)

    def __init__(self):
        super(BaseCustomNode, self).__init__()
        self.is_exec = False

    @property
    def isViableStartNode(self):
        return self.is_exec

    @property
    def importLines(self):
        return []

    @property
    def fullClassName(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}"

    def getFunctionName(self):
        return f"{self.fullClassName}.execute"

    def getModule(self):
        return self.__class__.__module__

    def getDefaultInput(self, port):
        prop = self.get_property(self.getPropertyName(port.name()))
        if prop == '':
            prop = None

        if isinstance(prop, str):
            return '{!r}'.format(prop)[1:-1]

        return prop

    def getPropertyName(self, name):
        return f"{PROPERTY_PREFIX}{name}"

    def add_or_update_input(self, name='input', default_value='', multi_input=False, display_name=True,
                  color=DEFAULT_PORT_COLOR):
        
        port = self.getInputPortByName(name)
        if port == None:
            port = super().add_input(name,multi_input, display_name,color)

        try:
            self.create_property(self.getPropertyName(name), default_value, widget_type=NODE_PROP_QLINEEDIT)
        except:
            self.set_property(self.getPropertyName(name), default_value)

        port.is_exec = False
        return port

    def add_input(self, name='input', default_value='', multi_input=False, display_name=True,
                  color=DEFAULT_PORT_COLOR):
        port = super().add_input(name,multi_input, display_name,color)
        self.create_property(self.getPropertyName(name), default_value, widget_type=NODE_PROP_QLINEEDIT)
        port.is_exec = False
        return port

    def clearOutputs(self):
        ports = self._outputs.copy()
        for p in ports:
            self.deletePort(p)

    def clearInputs(self):
        ports = self._inputs.copy()
        for p in ports:
            self.deletePort(p)

    @property
    def inputProperties(self):
        inputProps = dict()
        for key,val in self.model._custom_prop.items():
            if key in self.inputNames:
                inputProps[key] = val
            
        return inputProps

    @property
    def inputNames(self):
        return [p.name() for p in self._inputs]

    @property
    def outputNames(self):
        return [p.name() for p in self._outputs]

    def getOutputPortByName(self, name):
        ports = [p for p in self._outputs if p.name() == name]
        return ports[0] if len(ports) > 0 else None

    def getInputPortByName(self, name):
        ports = [p for p in self._inputs if p.name() == name]
        return ports[0] if len(ports) > 0 else None

    def deleteProperty(self, propertyName):
        del self.model._custom_prop[propertyName]

    def deletePort(self, port):
        portType = port.type_()
        
        if portType == IN_PORT:
            modelPorts = self.model.inputs
            ports = self._inputs
            items = self.view._input_items
            textItem = self.view.get_input_text_item(port.view)
        elif portType == OUT_PORT:
            modelPorts = self.model.outputs
            ports = self._outputs
            items = self.view._output_items
            textItem = self.view.get_output_text_item(port.view)

        self.graph.undo_stack().clear()

        try:
            self.deleteProperty(self.getPropertyName(port.name()))
        except:
            pass

        del modelPorts[self.getPropertyName(port.name())]
        ports.remove(port)

        connectedPorts = port.connected_ports().copy()

        for connectedPort in connectedPorts:
            self.disconnectPorts(port, connectedPort)

        nodeView = self.view
        portView = port.view
        portView.setParentItem(None)
        textItem.setParentItem(None)
        del items[portView]

        nodeView.post_init()

    def disconnectPorts(self, source: Port, target: Port):
        src_model = source.model
        trg_model = target.model
        src_id = source.node().id
        trg_id = target.node().id

        port_names = src_model.connected_ports.get(trg_id)
        if port_names is []:
            del src_model.connected_ports[trg_id]
        if port_names and target.name() in port_names:
            port_names.remove(target.name())

        port_names = trg_model.connected_ports.get(src_id)
        if port_names is []:
            del trg_model.connected_ports[src_id]
        if port_names and source.name() in port_names:
            port_names.remove(source.name())

        source.view.disconnect_from(target.view)

    def add_output(self, name='output', multi_output=True, display_name=True,
                color=DEFAULT_PORT_COLOR):
        port = super().add_output(name, multi_output, display_name, color)
        port.is_exec = False
        return port

    def add_exec_input(self, name):
        port = super().add_input(name,color=EXECUTE_PORT_COLOR)
        port.is_exec = True
        self.is_exec = True
        return port

    def add_exec_output(self, name):
        port = self.add_output(name, color=EXECUTE_PORT_COLOR, multi_output=False)
        port.is_exec = True
        self.is_exec = True
        return port

    def add_button(self, name, onClick):
        widget = NodeButton(onClick, parent=self.view, name=name)
        self.view.add_widget(widget)

    def add_combo_menu(self, name='', label='', items=None, tab=None):
        """
        Create a custom property and embed a
        :class:`PySide2.QtWidgets.QComboBox` widget into the node.

        Args:
            name (str): name for the custom property.
            label (str): label to be displayed.
            items (list[str]): items to be added into the menu.
            tab (str): name of the widget tab to display in.
        """
        items = items or []
        self.create_property(name, items[0] if len(items) > 0 else None, items=items, widget_type=node.NODE_PROP_QCOMBO, tab=tab)

        widget = node.NodeComboBox(self.view, name, label, items)
        widget.value_changed.connect(lambda k, v: self.set_property(k, v))
        self.view.add_widget(widget)

        return widget

    def addTextEdit(self, name='', label='', text='', tab=None):
            """
            Create a custom property and embed a
            :class:`PySide2.QtWidgets.QTextEdit` widget into the node.

            Args:
                name (str): name for the custom property.
                label (str): label to be displayed.
                text (str): pre filled text.
                tab (str): name of the widget tab to display in.
            """
            self.create_property(name, text, widget_type=NODE_PROP_QLINEEDIT, tab=tab)
            widget = TextEditNodeWidget(self.view, name, label, text)
            widget.value_changed.connect(lambda k, v: self.set_property(k, v))
            self.view.add_widget(widget)

            return widget

@excludeFromRegistration
class BaseCustomCodeNode(BaseCustomNode):
    """
    The BaseCustomCodeNode handles code generation manually.
    """

    __identifier__ = DEFAULT_IDENTIFIER
    NODE_NAME = 'Base Custom Code Node'

    def __init__(self):
        super(BaseCustomCodeNode, self).__init__()

    def generateCode(self, sourceCodeLines, indent):
        return 'None'

@excludeFromRegistration
class VariableInputCountNode(BaseCustomNode):
    """
    This node allows the user to specify a varying amount of inputs.
    """

    __identifier__ = DEFAULT_IDENTIFIER
    NODE_NAME = 'Variable Input Count Node'

    def __init__(self):
        super(VariableInputCountNode, self).__init__()

        self.count = 0
        self.inputCountInput = self.add_text_input(self.getPropertyName("inputCount"), "Input Count")
        self.inputCountInput.value_changed.connect(lambda k, v: self.refresh())

    def removePrefix(self, text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]

        return text

    def deserialize(self, data):
        # set properties.
        for prop in self.model.properties.keys():
            if prop in data.keys():
                self.model.set_property(prop, data[prop])

        # set custom properties.
        for prop, val in data.get('custom', {}).items():
            try:
                self.model.set_property(prop, val)
            except:
                self.add_input(self.removePrefix(prop, PROPERTY_PREFIX), default_value=val)

    def refresh(self):
        try:
            prevCount = self.count
            self.count = int(self.get_property(self.getPropertyName("inputCount")))
        except:
            print("Invalid count input.")
            return

        customProps = self.model._custom_prop.copy()

        # Delete ports if there are too many:
        if self.count < prevCount:
            for i in range(self.count, prevCount):
                n = f"in{i}"
                p = self.getInputPortByName(n)
                self.deletePort(p)

        for i in range(prevCount, self.count):
            self.add_or_update_input(f"in{i}", customProps.get(self.getPropertyName(f"in{i}")))

@excludeFromRegistration
class InlineNode(BaseCustomNode):
    """
    The inline node is expected to return one-line code.
    """

    __identifier__ = DEFAULT_IDENTIFIER
    NODE_NAME = 'Inline Node'

    def __init__(self):
        super(InlineNode, self).__init__()

    def getInlineCode(self):
        return 'None'

@excludeFromRegistration
class BaseExecuteNode(BaseCustomNode):
    """
    Execution nodes are handled specially by the python code generator.
    While the non-execution nodes are called implicitly when they are used for the first time,
    execution nodes are called explicitly in sequence based on their connection.

    Note: Non-execution nodes without an output pin won't be executed at all.
    """
    __identifier__ = DEFAULT_IDENTIFIER
    NODE_NAME = 'Base Execute Node'

    def __init__(self):
        super(BaseExecuteNode, self).__init__()

@excludeFromRegistration
class ExecuteNode(BaseExecuteNode):
    __identifier__ = DEFAULT_IDENTIFIER
    NODE_NAME = 'Execute Node'

    def __init__(self):
        super(ExecuteNode, self).__init__()

        self.add_exec_input('Execute')
        self.add_exec_output('Execute')

import ast
import inspect

def contains_explicit_return(f):
    try:
        return any(isinstance(node, ast.Return) for node in ast.walk(ast.parse(inspect.getsource(f))))
    except:
        return False

def defNode(name, isExecutable=False, returnNames=[], identifier=DEFAULT_IDENTIFIER):
    """
    Decorator for functions to allow easy node creation.
    Example (isExecutable=False):
    @defNode('Add', returnNames=['Sum'], identifier='Math')
    def add(lhs, rhs):
        return lhs + rhs

    Example (isExecutable=True):
    @defNode('Print', identifier='Display', isExecutable=True)
    def _print(value):
        print(value)
    """

    def wrapper(fn):
        signature = inspect.signature(fn)
        hasVariableNumberOfArguments = any(v.kind == inspect.Parameter.VAR_POSITIONAL for v in signature.parameters.values())

        class CustomNode(VariableInputCountNode if hasVariableNumberOfArguments else BaseCustomNode):
            __identifier__ = identifier
            NODE_NAME = name

            def __init__(self):
                super(CustomNode, self).__init__()

                if isExecutable:
                    self.add_exec_input('Execute')
                    self.add_exec_output('Execute')

                for returnName in returnNames:
                    self.add_output(returnName)

                if len(returnNames) == 0 and contains_explicit_return(fn):
                    self.add_output('return')
                
                for k, v in signature.parameters.items():
                    if not v.kind in [inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL]:
                        defaultValue = v.default if v.default is not inspect.Parameter.empty else ''
                        self.add_input(k, default_value=(f"\"{defaultValue}\"" if isinstance(defaultValue, str) else defaultValue))

            def getFunctionName(self):
                return f"{fn.__module__}.{fn.__name__}"

            def getModule(self):
                return fn.__module__

        CustomNode.__name__ = name.replace(" ", "")
        return fn
    return wrapper

def defInlineNode(name, isExecutable=False, returnNames=[], identifier=DEFAULT_IDENTIFIER):
    def wrapper(fn):
        class CustomInlineNode(InlineNode):
            __identifier__ = identifier
            NODE_NAME = name

            def __init__(self):
                super(CustomInlineNode, self).__init__()

                if isExecutable:
                    self.add_exec_input('Execute')
                    self.add_exec_output('Execute')

                for returnName in returnNames:
                    self.add_output(returnName)

                if len(returnNames) == 0 and contains_explicit_return(fn) and not isExecutable:
                    self.add_output('return')

                signature = inspect.signature(fn)
                for k, v in signature.parameters.items():
                    defaultValue = v.default if v.default is not inspect.Parameter.empty else ''
                    self.add_input(k, default_value=(f"\"{defaultValue}\"" if isinstance(defaultValue, str) else defaultValue))

            def getInlineCode(self, *args, **kwargs):
                return fn(*args, **kwargs)

        CustomInlineNode.__name__ = name.replace(" ", "")
        return fn
    return wrapper



class NodeButton(NodeBaseWidget):
    """
    NodeButton Node Widget.
    """

    def __init__(self, onClick, parent=None, name='', label=''):
        super(NodeButton, self).__init__(parent, name, label)
        self.btn = QtWidgets.QPushButton()
        self.btn.setText(name)
        self.btn.clicked.connect(onClick)
        group = _NodeGroupBox(label)

        group.add_node_widget(self.btn)
        group.setMaximumWidth(120)
        self.setWidget(group)

    @property
    def type_(self):
        return 'LineEditNodeWidget'

    @property
    def widget(self):
        return self.btn

    @property
    def value(self):
        return ''

    @value.setter
    def value(self, text=''):
        pass

    @property
    def has_property(self):
        return False