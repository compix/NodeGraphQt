from node_exec.base_nodes import defNode, defInlineNode

COMPARE_IDENTIFIER = 'Compare'

@defInlineNode('Greater', identifier=COMPARE_IDENTIFIER)
def greater(lhs, rhs):
    return f'{lhs} > {rhs}'

@defInlineNode('Greater Equals', identifier=COMPARE_IDENTIFIER)
def greaterEquals(lhs, rhs):
    return f'{lhs} >= {rhs}'

@defInlineNode('Less', identifier=COMPARE_IDENTIFIER)
def less(lhs, rhs):
    return f'{lhs} < {rhs}'

@defInlineNode('Less Equals', identifier=COMPARE_IDENTIFIER)
def lessEquals(lhs, rhs):
    return f'{lhs} <= {rhs}'

@defNode('Equals', identifier=COMPARE_IDENTIFIER)
def equals(lhs, rhs):
    return f'{lhs} == {rhs}'

