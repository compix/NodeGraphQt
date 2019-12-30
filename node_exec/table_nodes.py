from node_exec.base_nodes import defNode, defInlineNode

TABLE_IDENTIFIER = 'Table'

@defNode(name='Row Values', returnNames=['row values'], identifier=TABLE_IDENTIFIER)
def getRowValues(table, rowIndex):
    return table.getRowValues(rowIndex)

@defInlineNode(name='Number Of Columns', returnNames=['value'], identifier=TABLE_IDENTIFIER)
def getNumberOfColumns(table):
    return f'{table}.ncols'

@defInlineNode(name='Number Of Rows', returnNames=['value'], identifier=TABLE_IDENTIFIER)
def getNumberOfRows(table):
    return f'{table}.nrows'

@defNode(name='Get Cell Value', returnNames=['value'], identifier=TABLE_IDENTIFIER)
def getCellValue(table, rowIndex, colIndex):
    return table.getCellValue(rowIndex, colIndex)

@defNode(name='Test', returnNames=['v0', 'v1'], identifier=TABLE_IDENTIFIER)
def someTest():
    return 5, "Test"