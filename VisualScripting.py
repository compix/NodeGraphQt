import os
import sys
from node_exec import *
from node_exec import base_nodes
from node_exec import all_nodes

from NodeGraphQt import (NodeGraph,
                         BaseNode,
                         BackdropNode,
                         setup_context_menu)
from NodeGraphQt import QtWidgets, QtCore, PropertiesBinWidget, NodeTreeWidget, QtGui
from PySide2 import QtUiTools

# import example base_nodes from the "example_nodes" package
from example_nodes import basic_nodes, widget_nodes
from node_exec.GraphManager import GraphManager
import node_exec.NodeGraphQt_mod

class VisualScripting(object):
    def __init__(self, graphSerializationFolder, parentWindow=None):
        self.graph = NodeGraph()
        self.graphViewer = self.graph.viewer()

        # set up default menu and commands.
        self.fileMenu, self.editMenu = setup_context_menu(self.graph)

        graphSerializationFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), graphSerializationFolder)
        self.graphManager = GraphManager(graphSerializationFolder)

        self.initNodes()
        self.setupPropertiesBin()

        uiFilePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "graphQt.ui")
        uiFile = QtCore.QFile(uiFilePath)
        uiFile.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.window = loader.load(uiFile)

        self.splitter =  QtWidgets.QSplitter()
        self.window.bottomLayout.addWidget(self.splitter)
        self.splitter.addWidget(self.nodeTree)
        self.splitter.addWidget(self.graphViewer)
        self.splitter.addWidget(self.propertiesBin)

        self.setupMenuBar()

    def setupMenuBar(self):
        menuBar = QtWidgets.QMenuBar()
        sessionMenu = QtWidgets.QMenu("Session")
        menuBar.addMenu(self.fileMenu)
        menuBar.addMenu(self.editMenu)
        menuBar.addMenu(sessionMenu)
        menuBar.setMaximumHeight(20)

        self.saveAction = QtWidgets.QAction("Save")
        self.saveAction.triggered.connect(self.onSave)

        self.loadAction = QtWidgets.QAction("Load")
        self.loadAction.triggered.connect(self.onLoad)

        self.runAction = QtWidgets.QAction("Run")
        self.runAction.triggered.connect(self.onRun)
        self.runAction.setShortcut(QtGui.QKeySequence("R"))

        sessionMenu.addAction(self.saveAction)
        sessionMenu.addAction(self.loadAction)
        sessionMenu.addAction(self.runAction)

        self.window.verticalLayout.insertWidget(0, menuBar)

    def onRun(self):
        self.graphManager.executeGraph()
        
    def onSave(self):
        currentGraphName = self.graphManager.getSessionGraphName()
        graphName, ok = QtWidgets.QInputDialog().getText(self.window, "Save Graph", "Graph Name:", QtWidgets.QLineEdit.Normal, currentGraphName)

        if ok and graphName and len(graphName) > 0:
            self.graphManager.saveGraph(self.graph, graphName)

    def onLoad(self):
        availableGraphs = list(self.graphManager.availableGraphNames)
        graphName, ok = QtWidgets.QInputDialog().getItem(self.window, "Select the graph", "Graph name:", availableGraphs, editable=False)

        if ok:
            self.graphManager.loadGraph(self.graph, graphName)

    def setupPropertiesBin(self):
        self.propertiesBin = PropertiesBinWidget(node_graph=self.graph)
        self.propertiesBin.setWindowFlags(QtCore.Qt.Tool)

        # Show node properties on node-double-click:
        def showPropertyBin(node):
            if not self.propertiesBin.isVisible():
                self.propertiesBin.show()

        self.graph.node_double_clicked.connect(showPropertyBin)

    def initNodes(self):
        for n in base_nodes.NODES_TO_REGISTER:
            self.graph.register_node(n)
        
        self.graph.register_node(BackdropNode)

        self.nodeTree = NodeTreeWidget(node_graph=self.graph)
        self.nodeTree.update()

    def getAsDockWidget(self, parent):
        self.dockWidget = QtWidgets.QDockWidget("Visual Scripting", parent)
        self.dockWidget.setWidget(self.window)
        self.dockWidget.setObjectName("visualScriptingDockWidget")
        return self.dockWidget

    def saveWindowState(self, settings):
        settings.setValue("visual_scripting_splitter_sizes", self.splitter.saveState())
        
    def restoreWindowState(self, settings):
        self.splitter.restoreState(settings.value("visual_scripting_splitter_sizes"))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    visualScripting = VisualScripting("VisualScripting_SaveData")
    visualScripting.window.show()

    app.exec_()
