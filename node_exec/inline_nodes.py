from node_exec.base_nodes import InlineNode, excludeFromRegistration

CONSTEXPR_IDENTIFIER = 'Const'

@excludeFromRegistration
class ConstInputNode(InlineNode):
    __identifier__ = CONSTEXPR_IDENTIFIER
    NODE_NAME = 'Const Input Node'

    def __init__(self):
        super().__init__()

        #self.add_text_input('constant', 'Constant', tab='widgets')
        self.addTextEdit('constant', 'Constant', tab='widgets')
        self.add_output('return')

class ConstantStringNode(ConstInputNode):
    NODE_NAME = 'Constant String'

    def getInlineCode(self):
        return '{!r}'.format(self.get_property('constant'))

class ConstantIntNode(ConstInputNode):
    NODE_NAME = 'Constant Int'

    def getInlineCode(self):
        try:
            val = self.get_property('constant')
            int(val)
            return val
        except:
            return 'None'

class ConstantExpressionNode(ConstInputNode):
    NODE_NAME = 'Constant Expression'

    def getInlineCode(self):
        return self.get_property('constant')

