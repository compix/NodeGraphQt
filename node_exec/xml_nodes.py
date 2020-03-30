from node_exec.base_nodes import defNode
import xml.etree.cElementTree as ET
from collections import OrderedDict

imported = False
try:
    import xmltodict
    imported = True
except:
    print("Note: XML to dict nodes are not available because the xmltodict module is missing: pip install xmltodict")

IDENTIFIER = "XML"

if imported:
    @defNode("XML String as Dictionary", isExecutable=True, returnNames=["dict"], identifier = IDENTIFIER)
    def xmlStringToDict(xmlString=""):
        return xmltodict.parse(xmlString)

    @defNode("XML File as Dictionary", isExecutable=True, returnNames=["dict"], identifier = IDENTIFIER)
    def xmlFileToDict(xmlPath=""):
        try:
            with open(xmlPath, 'r') as f:
                return xmltodict.parse(f.read())
        except Exception as e:
            print(f"Warning: Failed to parse {xmlPath} : {str(e)}")
            return dict()

    def flattenDict(d):
        def items():
            for key, value in d.items():
                if isinstance(value, dict):
                    for subkey, subvalue in flattenDict(value).items():
                        yield key + "." + subkey, subvalue
                else:
                    yield key, value

        return OrderedDict(items())

    @defNode("XML File as flat Dictionary", isExecutable=True, returnNames=["dict"], identifier = IDENTIFIER)
    def xmlFileAsFlatDict(xmlPath=""):
        try:
            with open(xmlPath, 'r') as f:
                theDict = xmltodict.parse(f.read())

            return flattenDict(theDict)
        except Exception as e:
            print(f"Warning: Failed to parse {xmlPath}: {str(e)}")
            return dict()

def xmlToFlatDict(element, theDict):
    if len(element) > 0:
        for child in element:
            xmlToFlatDict(child, theDict)
    else:
        theDict[element.tag] = element.text

@defNode("XML File as simple flat Dictionary", isExecutable=True, returnNames=["dict"], identifier = IDENTIFIER)
def xmlFileAsSimpleFlatDict(xmlPath=""):
    rootElement = ET.parse(xmlPath).getroot()

    theDict = OrderedDict()
    xmlToFlatDict(rootElement, theDict)

    return theDict

@defNode("XML Root", isExecutable=False, returnNames=["root element"], identifier = IDENTIFIER)
def getXMLRoot(xmlPath=""):
    return ET.parse(xmlPath).getroot()
        
@defNode("XML Elements", isExecutable=False, returnNames=["elements"], identifier = IDENTIFIER)
def getXMLElements(xmlElement=None, key=""):
    return xmlElement.findall(key)

@defNode("XML Find", isExecutable=False, returnNames=["element"], identifier = IDENTIFIER)
def findXMLElement(xmlElement=None, key=""):
    return xmlElement.find(key)

@defNode("XML Find And Get Tag", isExecutable=False, returnNames=["tag"], identifier = IDENTIFIER)
def findXMLElementAndGetTag(xmlElement=None, key=""):
    return xmlElement.find(key).tag

@defNode("XML Find And Get Text", isExecutable=False, returnNames=["text"], identifier = IDENTIFIER)
def findXMLElementAndGetText(xmlElement=None, key=""):
    return xmlElement.find(key).text

@defNode("XML Element Value", isExecutable=False, returnNames=["value"], identifier = IDENTIFIER)
def getXMLElementValue(xmlElement=None, key=""):
    return xmlElement.get(key)

@defNode("XML Element Text", isExecutable=False, returnNames=["text"], identifier = IDENTIFIER)
def getXMLElementText(xmlElement=None, key=""):
    return xmlElement.text

@defNode("XML Element Tag", isExecutable=False, returnNames=["tag"], identifier = IDENTIFIER)
def getXMLElementTag(xmlElement=None, key=""):
    return xmlElement.tag



