from node_exec.base_nodes import defNode, BaseCustomNode, VariableInputCountNode
import re

STRING_IDENTIFIER = 'String'

class ConcatNode(VariableInputCountNode):
    __identifier__ = STRING_IDENTIFIER
    NODE_NAME = 'Concat'

    def __init__(self):
        super(ConcatNode, self).__init__()

        self.add_input("seperator")
        self.add_output("return")

    @staticmethod
    def execute(seperator, *argv):
        sep = seperator if seperator != None else ''
        return sep.join([(s if s != None else '') for s in argv])

@defNode('Remove Whitespace', returnNames=["str"], identifier=STRING_IDENTIFIER)
def removeWhiteSpace(value):
    return "".join(value.split())

@defNode('Strip', returnNames=["str"], identifier=STRING_IDENTIFIER)
def _strip(value):
    return value.strip()

@defNode('Split', returnNames=["str_list"], identifier=STRING_IDENTIFIER)
def _split(value, seperator):
    return value.split(None if seperator == '' else seperator)

@defNode('Is Empty or Whitespace', returnNames=["str"], identifier=STRING_IDENTIFIER)
def isEmptyOrWhitespace(value):
    return value == None or value == '' or value.isspace()

@defNode('Regex Match', returnNames=["MatchObj"], identifier=STRING_IDENTIFIER)
def regexMatch(pattern, string, flags):
    return re.match(pattern, string, flags=(0 if flags == None or flags == '' else flags))

@defNode('Regex Full Match', returnNames=["MatchObj"], identifier=STRING_IDENTIFIER)
def regexFullmatch(pattern, string, flags):
    return re.fullmatch(pattern, string, flags=(0 if flags == None or flags == '' else flags))

@defNode('Regex Search', returnNames=["MatchObj"], identifier=STRING_IDENTIFIER)
def regexSearch(pattern, string, flags):
    return re.search(pattern, string, flags=(0 if flags == None or flags == '' else flags))

@defNode('Regex Find All', returnNames=["MatchObjects"], identifier=STRING_IDENTIFIER)
def regexFindall(pattern, string, flags):
    return re.findall(pattern, string, flags=(0 if flags == None or flags == '' else flags))

@defNode('Regex Split', returnNames=["substring_list"], identifier=STRING_IDENTIFIER)
def regexSplit(pattern, string, flags):
    return re.split(pattern, string, flags=(0 if flags == None or flags == '' else flags))

@defNode('Regex Sub', returnNames=["str"], identifier=STRING_IDENTIFIER)
def regexSub(pattern, replacement, string, count, flags):
    if count == None or count == '':
        count = 0

    return re.sub(pattern, replacement, string, count=count, flags=(0 if flags == None or flags == '' else flags))

@defNode('Regex Find Iterator', returnNames=["iter"], identifier=STRING_IDENTIFIER)
def regexFindIter(pattern, string, flags):
    return re.finditer(pattern, string, flags=(0 if flags == None or flags == '' else flags))

@defNode('Regex Escape', returnNames=["str"], identifier=STRING_IDENTIFIER)
def regexEscape(pattern):
    return re.escape(pattern)

@defNode('Regex MatchObject Group', returnNames=["str"], identifier=STRING_IDENTIFIER)
def regexMatchObjectGroup(matchObject, groupIndex):
    return matchObject.group(groupIndex) if matchObject != None else None

@defNode('Regex MatchObject All Groups', returnNames=["groups"], identifier=STRING_IDENTIFIER)
def regexMatchObjectAllGroups(matchObject):
    return matchObject.groups() if matchObject != None else []
    
@defNode('Regex MatchObject Group Dict', returnNames=["dict"], identifier=STRING_IDENTIFIER)
def regexMatchObjectGroupDict(matchObject):
    return matchObject.groupdict() if matchObject != None else dict()