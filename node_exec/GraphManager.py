"""
Manages serialized visual graphs and their execution models.
"""

import node_exec.code_generator
import os
import json
import sys
import importlib
from pathlib import Path
from typing import List

class GraphSettings(object):
    def __init__(self, name, category, startNodeName, graphFolder):
        self.name = name
        self.category = "Default" if category == None else category
        self.startNodeName = startNodeName

        self.id = GraphSettings.getGraphId(self.category, self.name)
        self.dataFolder = os.path.join(graphFolder, self.relativePath)

    @property
    def relativePath(self):
        return os.path.join(self.category, self.name)

    @property
    def sharedGraphsFolder(self):
        return Path(self.dataFolder).parent.parent

    @staticmethod
    def loadFromSettings(settingsPath):
        try:
            with open(settingsPath, mode='r') as f:
                settings = json.load(f)

            graphName = settings.get("name")
            startNodeName = settings.get("startNodeName")
            category = settings.get("category")

            return GraphSettings(graphName, category, startNodeName, Path(os.path.dirname(settingsPath)).parent.parent)
        except Exception as e:
            print(f"Failed to load settings file: {str(e)}")

        return None

    @staticmethod
    def getGraphId(graphName, graphCategory):
        return f'{graphCategory}_{graphName}'

    def save(self, settingsPath):
        try:
            settings = dict()
            settings["name"] = self.name
            settings["startNodeName"] = self.startNodeName
            settings["category"] = self.category
            with open(settingsPath, mode='w+') as f:
                json.dump(settings, f)
        except Exception as e:
            print(e)

class Session(object):
    def __init__(self, graphSettings : GraphSettings, graph):
        self.graphSettings = graphSettings
        self.graph = graph

class GraphManager(object):
    GRAPHS_FOLDER = "Graphs"

    def __init__(self, serializationFolders, codeGenerator = None):
        self.codeGenerator = codeGenerator
        if codeGenerator == None:
            self.codeGenerator = node_exec.code_generator.CodeGenerator()

        self.setSerializationFolders(serializationFolders)

        self.curSession = None

    def normpath(self, path):
        return os.path.normpath(os.path.normcase(path))

    def updateSerializationFolders(self, folders):
        serFolderMap = map(self.normpath, self.serializationFolders)
        for folder in folders:
            folder = os.path.normpath(os.path.normcase(folder))
            if not folder in serFolderMap:
                self.addSerializationFolder(folder)

    def setSerializationFolders(self, folders):
        self.serializationFolders = folders
        for folder in self.serializationFolders:
            self.makeGraphsFolder(folder)

    def addSerializationFolder(self, folder):
        if not os.path.exists(folder):
            raise RuntimeError(f'Unknown location: {folder}')
        
        if self.normpath(folder) in map(self.normpath, self.serializationFolders):
            raise RuntimeError(f'The folder already exists in the list.')

        self.serializationFolders.append(folder)
        self.makeGraphsFolder(folder)

    def removeSerializationFolderByIndex(self, index):
        self.serializationFolders.pop(index)

    def removeSerializationFolder(self, folder):
        idx = -1
        folder = os.path.normpath(os.path.normcase(folder))
        for i in range(0,len(self.serializationFolders)):
            if os.path.normpath(os.path.normcase(self.serializationFolders[i])) == folder:
                idx = i

        if idx >= 0:
            self.removeSerializationFolderByIndex(idx)
        else:
            raise RuntimeError(f'Unknown folder: {folder}')

    def makeGraphsFolder(self, serializationFolder):
        graphsFolder = os.path.join(serializationFolder, GraphManager.GRAPHS_FOLDER)
        self.mkDir(graphsFolder)

    def mkDir(self, directory):
        if os.path.isdir(directory):
            return

        try:
            os.makedirs(directory)
        except Exception as e:
            print(str(e))
    
    def retrieveAvailableGraphSettings(self) -> List[GraphSettings]:
        graphSettings = []
        for serializationFolder in self.serializationFolders:
            graphFolder = os.path.join(serializationFolder, GraphManager.GRAPHS_FOLDER)
            for graphSettingsPath in Path(graphFolder).rglob("*_settings.json"):
                settings = GraphSettings.loadFromSettings(graphSettingsPath)
                if settings != None:
                    graphSettings.append(settings)

        return graphSettings

    def retrieveAvailableGraphIds(self):
        return [s.id for s in self.retrieveAvailableGraphSettings()]

    @property
    def graphCategoryToNamesMap(self):
        settings = self.retrieveAvailableGraphSettings()
        d = dict()
        for s in settings:
            if s.category in d.keys():
                d[s.category].append(s.name)
            else:
                d[s.category] = [s.name]

        return d

    def retrieveAvailableGraphNames(self):
        return [s.name for s in self.retrieveAvailableGraphSettings()]

    def getGraphDataFolder(self, graphSettings : GraphSettings):
        return graphSettings.dataFolder

    def getGraphFilePath(self, graphSettings : GraphSettings):
        return os.path.join(self.getGraphDataFolder(graphSettings), graphSettings.name + ".json")

    def getPythonCodePath(self, graphSettings : GraphSettings):
        moduleName = self.getModuleNameFromGraphName(graphSettings.name)
        return os.path.join(self.getGraphDataFolder(graphSettings), moduleName + ".py")

    def getSettingsPath(self, graphSettings : GraphSettings):
        return os.path.join(self.getGraphDataFolder(graphSettings), graphSettings.name + "_settings.json")

    def getSessionGraphName(self):
        return self.curSession.graphSettings.name if self.curSession != None else ""

    def getSessionStartNodeName(self):
        return self.curSession.graphSettings.startNodeName if self.curSession != None else ""

    def getSessionCategory(self):
        return self.curSession.graphSettings.category if self.curSession != None else ""

    def getSessionGraphFolder(self):
        return ""

    def getModuleNameFromGraphName(self, graphName):
        return graphName.replace(" ", "")

    def saveCurrentSession(self):
        if self.curSession != None:
            s = self.curSession.graphSettings
            self.saveGraph(self.curSession.graph, s.dataFolder, s.name, s.category, s.startNodeName)

    def doesGraphExist(self, graphName, graphCategory):
        graphId = GraphSettings.getGraphId(graphName, graphCategory)

        if graphId in self.retrieveAvailableGraphIds() and (self.curSession == None or self.curSession.graphSettings.name != graphName):
            return True
        
        return False

    def saveGraph(self, graph, visualScriptingSerializationFolder, graphName, graphCategory, startNodeName):
        graphFolder = os.path.join(visualScriptingSerializationFolder, GraphManager.GRAPHS_FOLDER)
        settings = GraphSettings(graphName, graphCategory, startNodeName, graphFolder)

        graphFolder = self.getGraphDataFolder(settings)
        self.mkDir(graphFolder)

        graph.save_session(self.getGraphFilePath(settings))
        startNode = graph.get_node_by_name(startNodeName)
        moduleName = self.getModuleNameFromGraphName(graphName)
        self.codeGenerator.generatePythonCode(graph, graphName, startNode, moduleName, graphFolder)

        settingsFile = self.getSettingsPath(settings)
        settings.save(settingsFile)

        self.curSession = Session(settings, graph)

    def loadGraph(self, graph, graphName : str, category : str):
        graphSettings = self.getGraphSettings(graphName, category)

        if graphSettings != None:
            graph.load_session(self.getGraphFilePath(graphSettings))
            self.curSession = Session(graphSettings, graph)

    def getGraphSettings(self, graphName : str, category : str):
        for s in self.retrieveAvailableGraphSettings():
            if s.name == graphName and s.category == category:
                return s

        return None
        
    def executeGraph(self):
        if self.curSession == None:
            return

        sessionSettings = self.curSession.graphSettings
        self.saveGraph(self.curSession.graph, sessionSettings.dataFolder, sessionSettings.name, 
                       sessionSettings.category, startNodeName=sessionSettings.startNodeName)

        sessionSettings = self.curSession.graphSettings
        moduleName = self.getModuleNameFromGraphName(sessionSettings.name)
        pythonFile = self.getPythonCodePath(sessionSettings)
        pathonFileDir = os.path.dirname(pythonFile)

        if not pathonFileDir in sys.path:
            sys.path.append(pathonFileDir)

        execModule = importlib.import_module(moduleName)
        importlib.reload(execModule)
        return execModule.execute()



        