import json
from node_exec.base_nodes import defNode
import os

IDENTIFIER = "Json"

@defNode("Json Load From String", isExecutable=True, identifier=IDENTIFIER)
def loadFromString(inputString):
    return json.loads(inputString)

@defNode("Json Load From File", isExecutable=True, identifier=IDENTIFIER)
def loadFromFile(file):
    return json.load(file)

@defNode("Json Load From File Path", isExecutable=True, identifier=IDENTIFIER)
def loadFromFilePath(filePath):
    if os.path.exists(filePath):
        with open(filePath, "r") as f:
            return json.load(f)
    else:
        return None

@defNode("Json Save To String", isExecutable=True, identifier=IDENTIFIER)
def saveToString(obj, indent=4, sortKeys=True):
    return json.dumps(obj, indent=indent, sort_keys=sortKeys)

@defNode("Json Save To File", isExecutable=True, identifier=IDENTIFIER)
def saveToFile(obj, file, indent=4, sortKeys=True):
    json.dump(obj, file, indent=indent, sort_keys=sortKeys)

@defNode("Json Save To File Path", isExecutable=True, identifier=IDENTIFIER)
def saveToFilePath(obj, filePath, indent=4, sortKeys=True):
    if os.path.exists(filePath):
        with open(filePath, "r") as f:
            json.dump(obj, f, indent=indent, sort_keys=sortKeys)
