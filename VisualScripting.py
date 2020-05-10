from node_exec.GraphManager import GraphManager

class VisualScripting(object):
    def __init__(self, graphSerializationFolders, codeGenerator=None):
        self.graphManager = GraphManager(graphSerializationFolders, codeGenerator=codeGenerator)

    def save(self, settings, dbManager):
        """
        Serializes the state in settings and/or in the database.

        input:
            - settings: Must support settings.setValue(key: str, value)
            - dbManager: MongoDBManager
        """
        settings.setValue("graph_serialization_folders", self.graphManager.serializationFolders)

    def load(self, settings, dbManager):
        """
        Loads the state from settings and/or the database.

        input:
            - settings: Must support settings.value(str)
            - dbManager: MongoDBManager
        """
        graphSerializationFolders = settings.value("graph_serialization_folders")

        if graphSerializationFolders != None:
            self.graphManager.setSerializationFolders(graphSerializationFolders)