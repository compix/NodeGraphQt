from node_exec.base_nodes import defNode, defInlineNode

COMPARE_IDENTIFIER = 'Compare'

@defInlineNode('Greater', returnNames=["greater"], identifier=COMPARE_IDENTIFIER)
def greater(lhs, rhs):
    return f'{lhs} > {rhs}'

@defInlineNode('Greater Equals', returnNames=["equals"], identifier=COMPARE_IDENTIFIER)
def greaterEquals(lhs, rhs):
    return f'{lhs} >= {rhs}'

@defInlineNode('Less', returnNames=["less"], identifier=COMPARE_IDENTIFIER)
def less(lhs, rhs):
    return f'{lhs} < {rhs}'

@defInlineNode('Less Equals', returnNames=["lessEquals"], identifier=COMPARE_IDENTIFIER)
def lessEquals(lhs, rhs):
    return f'{lhs} <= {rhs}'

@defInlineNode('Equals', returnNames=["equals"], identifier=COMPARE_IDENTIFIER)
def equals(lhs, rhs):
    return f'{lhs} == {rhs}'

@defNode('Select', returnNames=["selected"], identifier=COMPARE_IDENTIFIER)
def select(condition, trueValue, falseValue):
    return trueValue if condition else falseValue

