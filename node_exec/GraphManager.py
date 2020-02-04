"""
Manages serialized visual graphs and their execution models.
"""

import node_exec.code_generator
import os
from PySide2.QtWidgets import QMessageBox
import json
import sys
import importlib
from node_exec.code_generator import CodeGenerator

class Session(object):
    def __init__(self, graphName, graphCategory, startNodeName, graph):
        self.graphName = graphName
        self.graphCategory = "Default" if graphCategory == None else graphCategory
        self.startNodeName = startNodeName
        self.graph = graph

class GraphManager(object):
    GRAPHS_FOLDER = "Graphs"

    def __init__(self, serializationFolder, codeGenerator = None):
        self.codeGenerator = codeGenerator
        if codeGenerator == None:
            self.codeGenerator = CodeGenerator()
        
        self.serializationFolder = serializationFolder

        self.graphsFolder = os.path.join(serializationFolder, GraphManager.GRAPHS_FOLDER)
        self.mkDir(self.graphsFolder)

        #self.availableGraphFolders = self.retrieveAvailableGraphFolders()
        #self.availableGraphNames = self.retrieveAvailableGraphNames()

        self.curSession = None
        
    def mkDir(self, dir):
        if os.path.isdir(dir):
            return

        try:
            os.makedirs(dir)
        except Exception as e:
            print(str(e))
    
    def retrieveAvailableGraphFolders(self):
        graphFolders = set()
        dirList = next(os.walk(self.graphsFolder))[1]
        for dir in dirList:
            graphFolders.add(dir)

        return graphFolders

    @property
    def availableGraphFolders(self):
        return self.retrieveAvailableGraphFolders()

    @property
    def availableGraphNames(self):
        return self.retrieveAvailableGraphNames()

    @property
    def graphCategoryToNamesMap(self):
        d = dict()
        
        availableGraphNames = self.availableGraphNames
        for graphName in availableGraphNames:
            graphSettings = self.loadGraphSettings(graphName)
            category = graphSettings.get('category')

            if category == None:
                category = "Default"

            if category in d.keys():
                d[category].append(graphName)
            else:
                d[category] = [graphName]

        return d

    def retrieveAvailableGraphNames(self):
        graphNames = set()
        for folder in self.availableGraphFolders:
            graphNames.add(os.path.basename(folder))

        return graphNames

    def getGraphFolder(self, graphName):
        return os.path.join(self.graphsFolder, graphName)

    def getGraphFilePath(self, graphName):
        return os.path.join(self.getGraphFolder(graphName), graphName + ".json")

    def getPythonCodePath(self, graphName):
        return os.path.join(self.getGraphFolder(graphName), graphName + ".py")

    def getSettingsPath(self, graphName):
        return os.path.join(self.getGraphFolder(graphName), graphName + "_settings.json")

    def getSessionGraphName(self):
        return self.curSession.graphName if self.curSession != None else ""

    def getSessionStartNodeName(self):
        return self.curSession.startNodeName if self.curSession != None else ""

    def saveGraph(self, graph, graphName, graphCategory, startNodeName='Exec Start'):
        writeGraph = True
        if graphName in self.availableGraphFolders and (self.curSession == None or self.curSession.graphName != graphName):
            ret = QMessageBox.question(None, "Name already exists.", "Are you sure you want to overwrite the existing graph with the same name?")
            writeGraph = ret == QMessageBox.Yes

        if writeGraph:
            graphFolder = self.getGraphFolder(graphName)
            self.mkDir(graphFolder)

            graph.save_session(self.getGraphFilePath(graphName))
            startNode = graph.get_node_by_name(startNodeName)
            self.codeGenerator.generatePythonCode(graph, startNode, graphName, graphFolder)

            settingsFile = self.getSettingsPath(graphName)
            settingsDict = dict()
            settingsDict['start_node'] = startNodeName
            settingsDict['category'] = graphCategory
            with open(settingsFile, mode='w+') as f:
                json.dump(settingsDict, f)

            self.curSession = Session(graphName, graphCategory, startNodeName, graph)

    def loadGraph(self, graph, graphName):
        graph.load_session(self.getGraphFilePath(graphName))

        with open(self.getSettingsPath(graphName), mode='r') as f:
            settings = json.load(f)
            self.curSession = Session(graphName, settings.get('category'), settings['start_node'], graph)

    def loadGraphSettings(self, graphName):
        settings = None

        with open(self.getSettingsPath(graphName), mode='r') as f:
            settings = json.load(f)

        return settings
        
    def executeGraph(self):
        if self.curSession == None:
            QMessageBox.critical(None, "Unsaved state", "Please save the graph first.")
            return

        self.saveGraph(self.curSession.graph, self.curSession.graphName, self.curSession.graphCategory, startNodeName=self.curSession.startNodeName)

        pythonFile = self.getPythonCodePath(self.curSession.graphName)
        pathonFileDir = os.path.dirname(pythonFile)

        if not pathonFileDir in sys.path:
            sys.path.append(pathonFileDir)

        execModule = importlib.import_module(self.curSession.graphName)
        importlib.reload(execModule)
        return execModule.execute()



        