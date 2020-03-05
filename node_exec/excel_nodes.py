from node_exec.base_nodes import defNode, defInlineNode
from node_exec.base_nodes import BaseCustomNode, BaseExecuteNode, InlineNode, BaseCustomCodeNode
from node_exec import code_generator
import os 

imported = False
try:
    import xlrd
    imported = True
except:
    print("Note: Excel Nodes are not available because the xlrd module is missing: pip install xlrd")

EXCEL_IDENTIFIER = 'Excel'

class ExcelTable:
    def __init__(self, sheet):
        self.sheet = sheet

    def getRowValues(self, rowIndex):
        return self.sheet.row_values(rowIndex) if self.sheet != None else []

    def getColumnValues(self, colIndex):
        return self.sheet.col_values(colIndex) if self.sheet != None else []

    def getColumnsWithoutHeader(self):
        return [self.getColumnValues(i)[1:] for i in range(0, self.ncols)]

    def getHeader(self,rowIndex=0):
        return self.getRowValues(rowIndex)

    @property
    def ncols(self):
        return self.sheet.ncols if self.sheet != None else 0

    @property
    def nrows(self):
        return self.sheet.nrows if self.sheet != None else 0

    def getRowsWithoutHeader(self):
        for rowIdx in range(1, self.nrows):
            yield self.getRowValues(rowIdx)

    def getCellValue(self, rowIndex, colIndex):
        return self.sheet.cell_value(rowIndex, colIndex) if self.sheet != None else None

    def getRowAsDict(self, headerValues, rowValues):
        return dict(zip(headerValues, rowValues))

if imported:
    class ExcelSheetProcessorNode(BaseCustomCodeNode):
        __identifier__ = EXCEL_IDENTIFIER
        NODE_NAME = 'Excel Sheet Processor'

        def __init__(self):
            super(ExcelSheetProcessorNode, self).__init__()

            self.add_exec_input('Execute')

            self.loop_body_port = self.add_exec_output('Iteration')
            self.loop_complete_port = self.add_exec_output('Completed')

            self.add_output('table')
            self.add_output('header')
            self.entry_port = self.add_output('entry as dict')

            #self.add_button("Refresh", self.refresh)

            self.workbookPathInput = self.add_input("workbookPath")
            self.sheetNameInput = self.add_input("sheetName")
            self.encodingInput = self.add_input("encodingOverride", default_value=None)
            self.headerRowIndexInput = self.add_input("headerRowIndex", default_value=0)

        def generateCode(self, sourceCodeLines, indent):
            inputParams = code_generator.getInputParamsSource(self)

            # Table output code:
            tableVar = code_generator.getVarNameSource(self, 0)
            tableCreationCode =  f"{self.fullClassName}.createTableFromSheetName({','.join(inputParams[0:-1])})"
            tableInitCode = code_generator.makeCodeLine(f"{tableVar} = {tableCreationCode}", indent)
            sourceCodeLines.append(tableInitCode)
            headerVar = code_generator.getVarNameSource(self, 1)
            sourceCodeLines.append(code_generator.makeCodeLine(f"{headerVar} = {tableVar}.getHeader({inputParams[-1]})", indent))

            # Loop body code:
            numNonExecOutputPorts = len(code_generator.getNonExecutionOutputPorts(self))
            tableValueVars = [code_generator.getVarNameSource(self, idx) for idx in range(3, max(numNonExecOutputPorts, 4))]
            preBodyLines = []
            loopVar = code_generator.getVarNameSource(self, idx=None)

            if len(self.entry_port.connected_ports()) > 0:
                entryAsDictVar = code_generator.getVarNameSource(self, 2)
                entryAsDictCode = f"{entryAsDictVar} = {tableVar}.getRowAsDict({headerVar}, {loopVar})"
                preBodyLines.append(code_generator.makeCodeLine(entryAsDictCode, indent + code_generator.DEFAULT_INDENT))
                
            collection = f"{tableVar}.getRowsWithoutHeader()"
            loopConditionCode = code_generator.makeCodeLine(f"for {loopVar} in {collection}:", indent)

            preBodyLines.append(code_generator.makeCodeLine(f"{','.join(tableValueVars)} = {loopVar}", indent + code_generator.DEFAULT_INDENT))
            code_generator.expandCodeWithCondition(self.loop_body_port, sourceCodeLines, loopConditionCode, indent, preBodyLines=preBodyLines)

            # Loop completion code:
            code_generator.expandExecCode(self.loop_complete_port, sourceCodeLines, indent)


        @staticmethod
        def createTableFromSheetName(workbookPath, sheetName, encodingOverride=None):
            if os.path.exists(workbookPath):
                return ExcelTable(xlrd.open_workbook(filename=workbookPath,encoding_override=encodingOverride).sheet_by_name(sheetName))
            else:
                print(f"Warning: The workbook file path \"{workbookPath}\" does not exist.")
                return ExcelTable(None)

        def refresh(self):
            try:
                workbookPath = code_generator.getDefaultInputParamSource(self, self.workbookPathInput)[1:-1]
                sheetName = code_generator.getDefaultInputParamSource(self, self.sheetNameInput)[1:-1]
                encodingOverride = code_generator.getDefaultInputParamSource(self, self.encodingInput)
                encodingOverride = encodingOverride[1:-1] if isinstance(encodingOverride, str) else None
                headerRowIndex = int(code_generator.getDefaultInputParamSource(self, self.headerRowIndexInput))

                self.table = ExcelTable(xlrd.open_workbook(filename=workbookPath,encoding_override=encodingOverride if encodingOverride != '' else None).sheet_by_name(sheetName))

                headerRow = self.table.getHeader(headerRowIndex)
                headerPortNames = self.outputNames[5:]

                for portName in headerPortNames:
                    if not portName in headerRow:
                        self.deletePort(self.getOutputPortByName(portName))

                for val in headerRow:
                    if not val in headerPortNames:
                        self.add_output(str(val))
                    else:
                        port = self.getOutputPortByName(val)
                        self._outputs.remove(port)
                        self._outputs.append(port)

                        item = self.view._output_items[port.view]
                        del self.view._output_items[port.view]
                        self.view._output_items[port.view] = item

                self.view.post_init()

            except:
                print("Excel Node: Incorrect input.")

    @defNode(name='Open Sheet', returnNames=['table'], identifier=EXCEL_IDENTIFIER)
    def openSheet(workbookPath, sheetName, encodingOverride=None):
        return ExcelTable(xlrd.open_workbook(filename=workbookPath,encoding_override=encodingOverride if encodingOverride != '' else None).sheet_by_name(sheetName))

    @defNode(name='Open Workbook', returnNames=['workbook'], identifier=EXCEL_IDENTIFIER)
    def openWorkbook(path, encodingOverride=None):
        return xlrd.open_workbook(filename=path,encoding_override=encodingOverride if encodingOverride != '' else None)

    @defNode(name='Sheet By Name', returnNames=['table'], identifier=EXCEL_IDENTIFIER)
    def getSheetByName(workbook, sheetName):
        return ExcelTable(workbook.sheet_by_name(sheetName))