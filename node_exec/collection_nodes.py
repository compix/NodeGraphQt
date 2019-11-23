from node_exec.base_nodes import defNode, defInlineNode

COLLECTION_IDENTIFIER = 'Collection'

@defNode('Append', isExecutable=True, identifier=COLLECTION_IDENTIFIER)
def append(collection, element):
    collection.append(element)
    return collection

@defInlineNode('Length', identifier=COLLECTION_IDENTIFIER)
def length(collection):
    return f'len({collection})'