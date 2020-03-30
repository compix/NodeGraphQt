from node_exec.base_nodes import defNode, defInlineNode

CORE_IDENTIFIER = 'Core'

@defNode(name='Variable', returnNames=["var"], isExecutable=True, identifier=CORE_IDENTIFIER)
def makeVar(initialValue=None):
    return initialValue

@defInlineNode(name='Assign', returnNames=["var"], isExecutable=True, identifier=CORE_IDENTIFIER)
def assign(lhs, rhs):
    return f'{lhs} = {rhs}'