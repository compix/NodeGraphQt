from node_exec.base_nodes import defNode, defInlineNode

CSV_IDENTIFIER = 'CSV'

class CSVTable:
    def __init__(self, path, separator, encodingOverride=None):
        self.rows = []
        with open(path) as f:
            for row in f:
                self.rows.append(row.rstrip('\n').split(sep=separator))

    def getRowValues(self, rowIndex):
        return self.rows[rowIndex]

    def getCellValue(self, rowIndex, colIndex):
        return self.rows[rowIndex][colIndex]

    @property
    def ncols(self):
        return len(self.rows[0]) if len(self.rows) > 0 else 0
    
    @property
    def nrows(self):
        return len(self.rows)

@defNode(name='Open CSV Table', returnNames=['table'], identifier=CSV_IDENTIFIER)
def openCSVTable(path, separator=';', encodingOverride=None):
    return CSVTable(path, separator, encodingOverride=encodingOverride)