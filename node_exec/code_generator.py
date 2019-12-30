"""
This module generates python code from a node graph.
"""

from os import path
from node_exec import base_nodes
from node_exec import flow_nodes

DEFAULT_INDENT = "    "

def isExecNode(node):
    return node.is_exec

def getExecuteSource(node, params):
    if isinstance(node, base_nodes.InlineNode):
        return node.getInlineCode(*params)
    else:
        return f"{node.getFunctionName()}({','.join(params)})"

def getVarNameSource(node,idx=0):
    return f"var_{node.id}_{idx}" if idx != None else f"var_{node.id}"

def getParamName(port):
    return getVarNameSource(port.connected_ports()[0].node())

def getInputParamsSource(node):
    params = []
    for inPort in node._inputs:
        if len(inPort.connected_ports()) > 0:
            srcOutputPort = inPort.connected_ports()[0]
            srcNode = srcOutputPort.node()
            
            if not inPort.is_exec:
                outputPortIdx = getNonExecutionOutputPorts(srcNode).index(srcOutputPort)
                varName = getVarNameSource(srcNode,idx=outputPortIdx)
                params.append(varName)
        else:
            params.append(node.getDefaultInput(inPort))
    
    return params

# Supports only one output but multiple inputs.
# Construct a call recursively by the following logic:
# node.execute(node.in[0].execute(), node.in[1].execute())
def generatePythonGetSourceCodeLines(node, sourceCodeLines, indent):
    # Recursion ends when base_nodes without input are reached or an execute node.
    if isExecNode(node):
        return

    codeLine = getExecuteSource(node, getInputParamsSource(node))
    for i in node._inputs:
        if len(i.connected_ports()) > 0:
            nextNode = i.connected_ports()[0].node()
            generatePythonGetSourceCodeLines(nextNode, sourceCodeLines, indent)

    varNames = [getVarNameSource(node, idx) for idx in range(0, len(getNonExecutionOutputPorts(node)))]
    varName = ','.join(varNames)
    codeLine = f"{indent}{varName} = {codeLine}"
        
    if not codeLine in sourceCodeLines:
        sourceCodeLines.append(codeLine)

def generateParamSourceCodeLines(node, sourceCodeLines, indent):
    for i in node._inputs:
        if not i.is_exec and len(i.connected_ports()) > 0:
            n = i.connected_ports()[0].node()
            generatePythonGetSourceCodeLines(n, sourceCodeLines, indent)

def getNextExecNode(port):
    return port.connected_ports()[0].node() if len(port.connected_ports()) > 0 else None

def getExecOutNode(node):
    for out in node._outputs:
        if out.is_exec:
            if len(out.connected_ports()) == 0:
                return None

            return out.connected_ports()[0].node()

    return None

def makeCodeLine(code, indent):
    return indent + code

def expandExecCode(execPort, sourceCodeLines, indent):
    nextNode = getNextExecNode(execPort)
    if not nextNode is None:
        generatePythonExecutionSourceCodeLines(nextNode, sourceCodeLines, indent)

def expandCodeWithCondition(execPort, sourceCodeLines, conditionalLine, indent, preBodyLines=[]):
    """
    Expands the code with a condition check line and a body.

    Args:
        execPort: The execution port to extract the next node and continue code generation.
                  If the next execution node is None the body consists of pass statement otherwise the body is empty.
        sourceCodeLines: The current source code lines that will be extended.
        conditionalLine (str): The code line with a condition (e.g. if or loop condition).
        indent (str): The current indentation level.
    """

    nextNode = getNextExecNode(execPort)
    sourceCodeLines.append(conditionalLine)

    sourceCodeLines += preBodyLines

    if not nextNode is None:
        generatePythonExecutionSourceCodeLines(nextNode, sourceCodeLines, indent + DEFAULT_INDENT)
    else:
        sourceCodeLines.append(makeCodeLine("pass", indent + DEFAULT_INDENT))

def handleForLoopSourceCodeLines(node, sourceCodeLines, indent):
    loopVar = getVarNameSource(node)
    loopStart = getParamName(node.in_start)
    loopEnd = getParamName(node.in_end)

    # Loop body code:    
    loopConditionCode = makeCodeLine(f"for {loopVar} in range({loopStart},{loopEnd}):", indent)
    expandCodeWithCondition(node.loop_body_port, sourceCodeLines, loopConditionCode, indent)

    # Loop completion code:
    expandExecCode(node.loop_complete_port, sourceCodeLines, indent)

def handleForEachLoopSourceCodeLines(node, sourceCodeLines, indent):
    loopVar = getVarNameSource(node)
    collection = getParamName(node._in)
    
    # Loop body code:    
    loopConditionCode = makeCodeLine(f"for {loopVar} in {collection}:", indent)
    expandCodeWithCondition(node.loop_body_port, sourceCodeLines, loopConditionCode, indent)

    # Loop completion code:
    expandExecCode(node.loop_complete_port, sourceCodeLines, indent)

def handleWhileLoopNodeSourceCodeLines(node, sourceCodeLines, indent):
    # Check the condition, execute the code and then update the condition variables:
    loopConditionVar = getParamName(node.condition_port)
    loopConditionCode = makeCodeLine(f"while {loopConditionVar}:", indent)
    expandCodeWithCondition(node.loop_body_port, sourceCodeLines, loopConditionCode, indent)
    generateParamSourceCodeLines(node, sourceCodeLines, indent + DEFAULT_INDENT)

    expandExecCode(node.loop_complete_port, sourceCodeLines, indent)

def handleIfNodeSourceCodeLines(node, sourceCodeLines, indent):
    condition = getParamName(node._in)
    ifCondition = makeCodeLine(f"if {condition}:", indent)
    expandCodeWithCondition(node.truePort, sourceCodeLines, ifCondition, indent)

    elseCondition = makeCodeLine("else:", indent)
    expandCodeWithCondition(node.falsePort, sourceCodeLines, elseCondition, indent)

def getNonExecutionOutputPorts(node):
    ports = []
    for port in node._outputs:
        if not port.is_exec:
            ports.append(port)

    return ports

def generatePythonExecutionSourceCodeLines(node, sourceCodeLines, indent = ""):
    if node == None:
        return

    generateParamSourceCodeLines(node, sourceCodeLines, indent)

    if isinstance(node, base_nodes.BaseCustomCodeNode):
        node.generateCode(sourceCodeLines, indent)
    elif isinstance(node, flow_nodes.ForLoopNode):
        handleForLoopSourceCodeLines(node, sourceCodeLines, indent)
    elif isinstance(node, flow_nodes.ForEachLoopNode):
        handleForEachLoopSourceCodeLines(node, sourceCodeLines, indent)
    elif isinstance(node, flow_nodes.IfNode):
        handleIfNodeSourceCodeLines(node, sourceCodeLines, indent)
    elif isinstance(node, flow_nodes.WhileLoopNode):
        handleWhileLoopNodeSourceCodeLines(node, sourceCodeLines, indent)
    else:
        codeLine = getExecuteSource(node, getInputParamsSource(node))
        if len(getNonExecutionOutputPorts(node)) > 0:
            varNames = [getVarNameSource(node, idx) for idx in range(0, len(getNonExecutionOutputPorts(node)))]
            varName = ','.join(varNames)
            codeLine =  f"{varName} = {codeLine}"
        sourceCodeLines.append(makeCodeLine(codeLine, indent))
        generatePythonExecutionSourceCodeLines(getExecOutNode(node), sourceCodeLines, indent)

def generatePythonCode(graph, node, moduleName, execFuncName, targetFolder):
    sourceCodeLines = []
    generatePythonExecutionSourceCodeLines(node, sourceCodeLines)

    # Create an empty python file with the name moduleName:
    #curFolder = path.dirname(path.abspath(__file__))
    #srcFilePath = path.join(curFolder, "../test")
    srcFilePath = path.join(targetFolder, moduleName + ".py")
    srcFile = open(srcFilePath,"w+")

    # Generate imports:
    importLines = []
    for n in graph.all_nodes():
        try:
            importLine = f"import {n.getModule()}"
            if not importLine in importLines:
                importLines.append(importLine)
        except:
            pass

    sourceCode = "\n".join(importLines)

    # Append source code lines:
    sourceCode += "\n\ndef " + execFuncName + "():\n"
    for line in sourceCodeLines:
        sourceCode += DEFAULT_INDENT + line + "\n"

    srcFile.write(sourceCode)

    srcFile.close()

    return srcFilePath