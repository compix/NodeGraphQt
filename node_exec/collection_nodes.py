from node_exec.base_nodes import defNode, defInlineNode

COLLECTION_IDENTIFIER = 'Collection'

@defNode('Append', isExecutable=True, identifier=COLLECTION_IDENTIFIER)
def append(collection, element):
    collection.append(element)
    return collection

@defInlineNode('Length', identifier=COLLECTION_IDENTIFIER)
def length(collection):
    return f'len({collection})'

@defInlineNode('Get Dict Value', identifier=COLLECTION_IDENTIFIER)
def getDictValue(dictionary, key, default):
    return f'{dictionary}.get({key}, {default})'

@defInlineNode('Contains', identifier=COLLECTION_IDENTIFIER)
def contains(collection, key):
    return f'{key} in {collection}'

@defInlineNode('Get Value By Index', identifier=COLLECTION_IDENTIFIER)
def getValueByIndex(collection, index):
    return f'{collection}[{index}]' 

