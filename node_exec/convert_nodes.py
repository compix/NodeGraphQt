from node_exec.base_nodes import defNode

CONVERSION_IDENTIFIER = 'Convert'

@defNode(name='To Int', identifier=CONVERSION_IDENTIFIER)
def toInt(value):
    return int(value)

@defNode(name='To String', identifier=CONVERSION_IDENTIFIER)
def toString(value):
    return str(value)