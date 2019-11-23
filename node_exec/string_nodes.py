from node_exec.base_nodes import defNode

STRING_IDENTIFIER = 'String'

@defNode('Remove Whitespace', identifier=STRING_IDENTIFIER)
def removeWhiteSpace(value):
    return "".join(value.split())

@defNode('Strip', identifier=STRING_IDENTIFIER)
def _strip(value):
    return value.strip()