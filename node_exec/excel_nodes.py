from node_exec.base_nodes import defNode, defInlineNode
from node_exec.base_nodes import BaseCustomNode, BaseExecuteNode, InlineNode, BaseCustomCodeNode
from node_exec import code_generator

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
        return self.sheet.row_values(rowIndex)

    def getColumnValues(self, colIndex):
        return self.sheet.col_values(colIndex)

    def getColumnsWithoutHeader(self):
        return [self.getColumnValues(i)[1:] for i in range(0, self.ncols)]

    def getHeader(self):
        return self.getRowValues(0)

    @property
    def ncols(self):
        return self.sheet.ncols

    @property
    def nrows(self):
        return self.sheet.nrows

    def getRowsWithoutHeader(self):
        for rowIdx in range(1, self.nrows):
            yield self.getRowValues(rowIdx)

    def getCellValue(self, rowIndex, colIndex):
        return self.sheet.cell_value(rowIndex, colIndex)

    def getRowAsDict(self, headerValues, rowValues):
        return dict(zip(headerValues, rowValues))

if imported:
    class ExcelSheetProcessorNode(BaseCustomCodeNode):
        __identifier__ = EXCEL_IDENTIFIER
        NODE_NAME = 'Excel Sheet Processor Node'

        def __init__(self):
            super(ExcelSheetProcessorNode, self).__init__()

            self.add_exec_input('Execute')

            self.pathInput = self.add_text_input('path', 'Workbook Path')
            self.sheetInput = self.add_text_input('sheetName', 'Sheet Name')
            self.encodingOverrideInput = self.add_text_input('encodingOverride', 'Encoding Override')

            self.pathInput.value_changed.connect(lambda k, v: self.refresh())
            self.sheetInput.value_changed.connect(lambda k, v: self.refresh())
            self.encodingOverrideInput.value_changed.connect(lambda k, v: self.refresh())

        def generateCode(self, sourceCodeLines, indent):
            # Table output code:
            workbookPath = '{!r}'.format(self.get_property('path'))
            sheetName = '{!r}'.format(self.get_property('sheetName'))
            encodingOverride = self.get_property('encodingOverride')
            encoding_override={encodingOverride} if encodingOverride != '' else None
            tableVar = code_generator.getVarNameSource(self, 0)
            tableCreationCode =  f"{self.fullClassName}.createTableFromSheetName({workbookPath},{sheetName},{encoding_override})"
            tableInitCode = code_generator.makeCodeLine(f"{tableVar} = {tableCreationCode}", indent)
            sourceCodeLines.append(tableInitCode)
            headerVar = code_generator.getVarNameSource(self, 1)
            sourceCodeLines.append(code_generator.makeCodeLine(f"{headerVar} = {tableVar}.getHeader()", indent))

            # Loop body code:
            tableValueVars = [code_generator.getVarNameSource(self, idx) for idx in range(3, len(code_generator.getNonExecutionOutputPorts(self)))]
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
            return ExcelTable(xlrd.open_workbook(filename=workbookPath,encoding_override=encodingOverride).sheet_by_name(sheetName))

        def refresh(self):
            self.firstCall = False
            self.clearOutputs()

            self.loop_body_port = self.add_exec_output('Iteration')
            self.loop_complete_port = self.add_exec_output('Completed')

            self.add_output('table')
            self.add_output('header')
            self.entry_port = self.add_output('entry as dict')

            workbookPath = self.get_property('path')
            sheetName = self.get_property('sheetName')
            encodingOverride = self.get_property('encodingOverride')

            try:
                self.table = ExcelTable(xlrd.open_workbook(filename=workbookPath,encoding_override=encodingOverride if encodingOverride != '' else None).sheet_by_name(sheetName))

                headerRow = self.table.getRowValues(0)

                for val in headerRow:
                    self.add_output(val)
            except:
                print("Excel Node: Incorrect input.")

    class ExcelSheetNode(InlineNode):
        __identifier__ = EXCEL_IDENTIFIER
        NODE_NAME = 'Excel Sheet Node'

        def __init__(self):
            super(ExcelSheetNode, self).__init__()

            self.pathInput = self.add_text_input('path', 'Workbook Path')
            self.sheetInput = self.add_text_input('sheetName', 'Sheet Name')
            self.encodingOverrideInput = self.add_text_input('encodingOverride', 'Encoding Override')

            self.pathInput.value_changed.connect(lambda k, v: self.refresh())
            self.sheetInput.value_changed.connect(lambda k, v: self.refresh())
            self.encodingOverrideInput.value_changed.connect(lambda k, v: self.refresh())

        @staticmethod
        def createFromSheetName(workbookPath, sheetName, encodingOverride=None):
            table = ExcelTable(xlrd.open_workbook(filename=workbookPath,encoding_override=encodingOverride).sheet_by_name(sheetName))
            return [table] + table.getColumnsWithoutHeader()

        def getInlineCode(self):
            workbookPath = '{!r}'.format(self.get_property('path'))
            sheetName = '{!r}'.format(self.get_property('sheetName'))
            encodingOverride = self.get_property('encodingOverride')
            encoding_override={encodingOverride} if encodingOverride != '' else None

            return f"{self.fullClassName}.createFromSheetName({workbookPath},{sheetName},{encoding_override})"

        def refresh(self):
            self.firstCall = False
            self.clearOutputs()

            self.add_output('table')

            workbookPath = self.get_property('path')
            sheetName = self.get_property('sheetName')
            encodingOverride = self.get_property('encodingOverride')

            try:
                self.table = ExcelTable(xlrd.open_workbook(filename=workbookPath,encoding_override=encodingOverride if encodingOverride != '' else None).sheet_by_name(sheetName))

                headerRow = self.table.getRowValues(0)

                for val in headerRow:
                    self.add_output(val)
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