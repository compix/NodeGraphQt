from node_exec.GraphManager import GraphManager

class VisualScripting(object):
    def __init__(self, graphSerializationFolder, codeGenerator=None):
        self.graphManager = GraphManager(graphSerializationFolder, codeGenerator=codeGenerator)