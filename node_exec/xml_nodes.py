from node_exec.base_nodes import defNode
import xml.etree.cElementTree as ET

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
            with open(xmlPath) as f:
                return xmltodict.parse(f)
        except:
            print(f"Warning: Failed to parse {xmlPath}")
            return dict()

@defNode("XML Root", isExecutable=False, returnNames=["root element"], identifier = IDENTIFIER)
def getXMLRoot(xmlPath=""):
    return ET.parse(xmlPath).getroot()
        
@defNode("XML Elements", isExecutable=False, returnNames=["elements"], identifier = IDENTIFIER)
def getXMLElements(xmlElement=None, key=""):
    return xmlElement.findall(key)
        
@defNode("XML Element Value", isExecutable=False, returnNames=["value"], identifier = IDENTIFIER)
def getXMLElementValue(xmlElement=None, key=""):
    return xmlElement.get(key)
 

