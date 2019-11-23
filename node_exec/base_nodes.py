from NodeGraphQt import BaseNode
from NodeGraphQt.constants import NODE_PROP_QLINEEDIT

DEFAULT_PORT_COLOR = (0,128,0)
EXECUTE_PORT_COLOR = (0,0,0)

NODES_TO_REGISTER = []

DEFAULT_IDENTIFIER = 'Default'

def excludeFromRegistration(cls):
    NODES_TO_REGISTER.remove(cls)
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
        NODES_TO_REGISTER.append(cls)

    def __init__(self):
        super(BaseCustomNode, self).__init__()
        self.is_exec = False

    def getFunctionName(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}.execute"

    def getModule(self):
        return self.__class__.__module__

    def getDefaultInput(self, port):
        prop = self.get_property(port.name())
        if is_float(prop) or is_int(prop):
            return prop
        else:
            return '{!r}'.format(prop)

    def add_input(self, name='input', multi_input=False, display_name=True,
                  color=DEFAULT_PORT_COLOR):
        port = super().add_input(name,multi_input, display_name,color)
        self.create_property(name, '', widget_type=NODE_PROP_QLINEEDIT)
        port.is_exec = False
        return port

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
        port = self.add_output(name, color=EXECUTE_PORT_COLOR)
        port.is_exec = True
        self.is_exec = True
        return port

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
    return any(isinstance(node, ast.Return) for node in ast.walk(ast.parse(inspect.getsource(f))))

def defNode(name, isExecutable=False, identifier=DEFAULT_IDENTIFIER):
    """
    Decorator for functions to allow easy node creation.
    Example (isExecutable=False):
    @defNode('Add', identifier='Math')
    def add(lhs, rhs):
        return lhs + rhs

    Example (isExecutable=True):
    @defNode('Print', identifier='Display', isExecutable=True)
    def _print(value):
        print(value)
    """

    def wrapper(fn):
        class CustomNode(BaseCustomNode):
            __identifier__ = identifier
            NODE_NAME = name

            def __init__(self):
                super(CustomNode, self).__init__()

                if isExecutable:
                    self.add_exec_input('Execute')
                    self.add_exec_output('Execute')

                if contains_explicit_return(fn):
                    self.add_output('return')

                for param in fn.__code__.co_varnames:
                    self.add_input(param)

            def getFunctionName(self):
                return f"{fn.__module__}.{fn.__name__}"

            def getModule(self):
                return fn.__module__

        CustomNode.__name__ = name.replace(" ", "")
        return fn
    return wrapper

def defInlineNode(name, isExecutable=False, identifier=DEFAULT_IDENTIFIER):
    def wrapper(fn):
        class CustomInlineNode(InlineNode):
            __identifier__ = identifier
            NODE_NAME = name

            def __init__(self):
                super(CustomInlineNode, self).__init__()

                if isExecutable:
                    self.add_exec_input('Execute')
                    self.add_exec_output('Execute')

                if contains_explicit_return(fn) and not isExecutable:
                    self.add_output('return')

                for param in fn.__code__.co_varnames:
                    self.add_input(param)

            def getInlineCode(self, *args, **kwargs):
                return fn(*args, **kwargs)

        CustomInlineNode.__name__ = name.replace(" ", "")
        return fn
    return wrapper