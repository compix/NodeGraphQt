from node_exec.base_nodes import defNode, defInlineNode

COLLECTION_IDENTIFIER = 'Collection'

@defNode('Append', returnNames=["collection"], isExecutable=True, identifier=COLLECTION_IDENTIFIER)
def append(collection, element):
    collection.append(element)
    return collection

@defInlineNode('Length', returnNames=["len"], identifier=COLLECTION_IDENTIFIER)
def length(collection):
    return f'len({collection})'

@defInlineNode('Get Dict Value', returnNames=["value"], identifier=COLLECTION_IDENTIFIER)
def getDictValue(dictionary, key, default):
    return f'{dictionary}.get({key}, {default})'

@defInlineNode('Contains', returnNames=["contains"], identifier=COLLECTION_IDENTIFIER)
def contains(collection, key):
    return f'{key} in {collection}'

@defInlineNode('Get Value By Index', returnNames=["value"], identifier=COLLECTION_IDENTIFIER)
def getValueByIndex(collection, index):
    return f'{collection}[{index}]' 

@defInlineNode('Merge Dictionaries', returnNames=["dict"], identifier=COLLECTION_IDENTIFIER)
def mergeDicts(dict0, dict1):
    return "{" + f'**{dict0}, **{dict1}' + "}"

@defNode('Add Dictionary Entry', returnNames=["dict"], isExecutable=True, identifier=COLLECTION_IDENTIFIER)
def addDictEntry(dictionary, key, value):
    dictionary[key] = value
    return dictionary

@defNode('Remove Dictionary Key', returnNames=["key"], isExecutable=True, identifier=COLLECTION_IDENTIFIER)
def removeDictKey(dictionary, key):
    '''
    Returns the removed key. If the key does not exist None is returned.
    '''
    return dictionary.pop(key, None)

@defInlineNode('Create Dictionary', isExecutable=True, returnNames=['dict'], identifier=COLLECTION_IDENTIFIER)
def createDict():
    return 'dict()'

@defInlineNode('Create List', isExecutable=True, returnNames=['list'], identifier=COLLECTION_IDENTIFIER)
def createList():
    return '[]'