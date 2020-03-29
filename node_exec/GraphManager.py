"""
Manages serialized visual graphs and their execution models.
"""

import node_exec.code_generator
import os
from PySide2.QtWidgets import QMessageBox
import json
import sys
import importlib
from pathlib import Path
from typing import List

class GraphSettings(object):
    def __init__(self, name, category, startNodeName):
        self.name = name
        self.category = "Default" if category == None else category
        self.startNodeName = startNodeName

        self.id = self.category + "_" + self.name
        self.relativePath = os.path.join(category, name)

    def setRelativePath(self, relativePath):
        self.relativePath = relativePath

    @staticmethod
    def loadFromSettings(settingsPath):
        try:
            with open(settingsPath, mode='r') as f:
                settings = json.load(f)

            graphName = settings.get("name")
            startNodeName = settings.get("startNodeName")
            category = settings.get("category")

            return GraphSettings(graphName, category, startNodeName)
        except Exception as e:
            print(f"Failed to load settings file: {str(e)}")

        return None

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

    def __init__(self, serializationFolder, codeGenerator = None):
        self.codeGenerator = codeGenerator
        if codeGenerator == None:
            self.codeGenerator = node_exec.code_generator.CodeGenerator()

        self.codeGenerator.setGraphManager(self)
        self.serializationFolder = serializationFolder

        self.graphsFolder = os.path.join(serializationFolder, GraphManager.GRAPHS_FOLDER)
        self.mkDir(self.graphsFolder)

        self.curSession = None
        
        # TODO:
        # 1. Save with category as subfolder
        # 2. Retrieve settings info instead of just the graph names.

    def mkDir(self, directory):
        if os.path.isdir(directory):
            return

        try:
            os.makedirs(directory)
        except Exception as e:
            print(str(e))
    
    def retrieveAvailableGraphSettings(self) -> List[GraphSettings]:
        graphSettings = []
        for graphSettingsPath in Path(self.graphsFolder).rglob("*_settings.json"):
            settings = GraphSettings.loadFromSettings(graphSettingsPath)
            if settings != None:
                graphSettings.append(settings)
                settings.setRelativePath(os.path.dirname(os.path.relpath(graphSettingsPath, self.graphsFolder)))

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

    def getGraphFolder(self, graphSettings : GraphSettings):
        return os.path.join(self.graphsFolder, graphSettings.relativePath)

    def getGraphFilePath(self, graphSettings : GraphSettings):
        return os.path.join(self.getGraphFolder(graphSettings), graphSettings.name + ".json")

    def getPythonCodePath(self, graphSettings : GraphSettings):
        moduleName = self.getModuleNameFromGraphName(graphSettings.name)
        return os.path.join(self.getGraphFolder(graphSettings), moduleName + ".py")

    def getSettingsPath(self, graphSettings : GraphSettings):
        return os.path.join(self.getGraphFolder(graphSettings), graphSettings.name + "_settings.json")

    def getSessionGraphName(self):
        return self.curSession.graphSettings.name if self.curSession != None else ""

    def getSessionStartNodeName(self):
        return self.curSession.graphSettings.startNodeName if self.curSession != None else ""

    def getModuleNameFromGraphName(self, graphName):
        return graphName.replace(" ", "")

    def saveGraph(self, graph, graphName, graphCategory, startNodeName='Exec Start'):
        writeGraph = True

        settings = GraphSettings(graphName, graphCategory, startNodeName)
        graphId = settings.id

        if graphId in self.retrieveAvailableGraphIds() and (self.curSession == None or self.curSession.graphSettings.name != graphName):
            ret = QMessageBox.question(None, "Name already exists.", "Are you sure you want to overwrite the existing graph with the same name?")
            writeGraph = ret == QMessageBox.Yes

        if writeGraph:
            graphFolder = self.getGraphFolder(settings)
            self.mkDir(graphFolder)

            graph.save_session(self.getGraphFilePath(settings))
            startNode = graph.get_node_by_name(startNodeName)
            moduleName = self.getModuleNameFromGraphName(graphName)
            self.codeGenerator.generatePythonCode(graph, startNode, moduleName, graphFolder)

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
            QMessageBox.critical(None, "Unsaved state", "Please save the graph first.")
            return

        sessionSettings = self.curSession.graphSettings
        self.saveGraph(self.curSession.graph, sessionSettings.name, sessionSettings.category, startNodeName=sessionSettings.startNodeName)

        sessionSettings = self.curSession.graphSettings
        moduleName = self.getModuleNameFromGraphName(sessionSettings.name)
        pythonFile = self.getPythonCodePath(sessionSettings)
        pathonFileDir = os.path.dirname(pythonFile)

        if not pathonFileDir in sys.path:
            sys.path.append(pathonFileDir)

        execModule = importlib.import_module(moduleName)
        importlib.reload(execModule)
        return execModule.execute()



        