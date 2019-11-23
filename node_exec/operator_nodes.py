from node_exec.base_nodes import defNode, defInlineNode

OPERATOR_IDENTIFIER = 'Operator'

@defInlineNode('Add', identifier=OPERATOR_IDENTIFIER)
def add(lhs, rhs):
    return f'{lhs} + {rhs}'

@defInlineNode('Multiply', identifier=OPERATOR_IDENTIFIER)
def multiply(lhs, rhs):
    return f'{lhs} * {rhs}'

@defInlineNode('Divide', identifier=OPERATOR_IDENTIFIER)
def divide(lhs, rhs):
    return f'{lhs} / {rhs}'

@defInlineNode('Subtract', identifier=OPERATOR_IDENTIFIER)
def subtract(lhs, rhs):
    return f'{lhs} - {rhs}'