from node_exec.base_nodes import defNode, defInlineNode, BaseCustomNode

OPERATOR_IDENTIFIER = 'Operator'

class AddMultipleNode(BaseCustomNode):
    __identifier__ = OPERATOR_IDENTIFIER
    NODE_NAME = 'Add Multiple'

    def __init__(self):
        super(AddMultipleNode, self).__init__()

        self.inputCountInput = self.add_text_input("inputCount", "Input Count")
        self.inputCountInput.value_changed.connect(lambda k, v: self.refresh())

        self.add_output("sum")

    def refresh(self):
        try:
            count = int(self.get_property("inputCount"))
        except:
            print("Invalid count input.")
            return

        self.clearInputs()

        for i in range(0, count):
            self.add_input(f"in{i}")

    @staticmethod
    def execute(*argv):
        return sum(argv)

@defInlineNode('Add', returnNames=["sum"], identifier=OPERATOR_IDENTIFIER)
def add(lhs, rhs):
    return f'{lhs} + {rhs}'

@defInlineNode('Multiply', returnNames=["product"], identifier=OPERATOR_IDENTIFIER)
def multiply(lhs, rhs):
    return f'{lhs} * {rhs}'

@defInlineNode('Divide', returnNames=["quotient"], identifier=OPERATOR_IDENTIFIER)
def divide(lhs, rhs):
    return f'{lhs} / {rhs}'

@defInlineNode('Subtract', returnNames=["difference"], identifier=OPERATOR_IDENTIFIER)
def subtract(lhs, rhs):
    return f'{lhs} - {rhs}'