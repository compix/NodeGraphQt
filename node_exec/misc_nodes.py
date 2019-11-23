from node_exec.base_nodes import BaseExecuteNode, ExecuteNode, defNode, BaseCustomNode, InlineNode
from NodeGraphQt.widgets.node_property import NodeLineEdit

MISC_IDENTIFIER = 'Misc'

class ExecStart(BaseExecuteNode):
    __identifier__ = MISC_IDENTIFIER
    NODE_NAME = 'Exec Start'

    def __init__(self):
        super(ExecStart, self).__init__()

        self.add_exec_output("Execute")

    @staticmethod
    def execute():
        pass

class PythonStatementNode(InlineNode):
    __identifier__ = MISC_IDENTIFIER
    NODE_NAME = 'Python Statement'

    def __init__(self):
        super(PythonStatementNode, self).__init__()

        self.add_exec_input('Execute')
        self.add_exec_output('Execute')

        self.add_text_input('code', 'Code', tab='widgets')

    def getInlineCode(self):
        return self.get_property('code')

@defNode('Print', identifier=MISC_IDENTIFIER, isExecutable=True)
def _print(value):
    print(value)

