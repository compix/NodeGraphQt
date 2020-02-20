import os
import sys
import node_exec.nodes_cfg
node_exec.nodes_cfg.init()

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
from PySide2.QtWidgets import QDialog
from PySide2.QtCore import Qt
from PySide2.QtGui import QStandardItemModel, QStandardItem

class VisualScripting(object):
    def __init__(self, graphSerializationFolder, parentWindow=None, codeGenerator=None):
        self.graph = NodeGraph()
        self.graphViewer = self.graph.viewer()

        # set up default menu and commands.
        self.fileMenu, self.editMenu = setup_context_menu(self.graph)

        self.graphManager = GraphManager(graphSerializationFolder, codeGenerator=codeGenerator)

        self.initNodes()
        self.setupPropertiesBin()

        self.window = self.loadUI("graphQt.ui")

        self.splitter =  QtWidgets.QSplitter()
        self.window.bottomLayout.addWidget(self.splitter)
        self.splitter.addWidget(self.nodeTree)
        self.splitter.addWidget(self.graphViewer)
        self.splitter.addWidget(self.propertiesBin)

        self.setupMenuBar()

    def loadUI(self, relUIPath):
        uiFilePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), relUIPath)
        uiFile = QtCore.QFile(uiFilePath)
        uiFile.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        return loader.load(uiFile)

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
        
    def setupCategoryComboBox(self, comboBox):
        categories = self.graphManager.graphCategoryToNamesMap.keys()
        for category in categories:
            comboBox.addItem(category)

    def loadDialog(self, relUIPath) -> QDialog:
        dialog = self.loadUI(relUIPath)
        dialog.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        return dialog

    def onSave(self):
        currentGraphName = self.graphManager.getSessionGraphName()
        currentStartNodeName = self.graphManager.getSessionStartNodeName()

        dialog = self.loadDialog("saveGraphDialog.ui")
        dialog.graphNameLineEdit.setText(currentGraphName)
        self.setupCategoryComboBox(dialog.categoryComboBox)

        allGraphNodeNames = [n.name() for n in self.graph.all_nodes() if n.isViableStartNode]
        for n in allGraphNodeNames:
            dialog.startNodeComboBox.addItem(n)
        
        if currentStartNodeName in allGraphNodeNames:
            dialog.startNodeComboBox.setCurrentText(currentStartNodeName)

        ok = dialog.exec_()
        graphName = dialog.graphNameLineEdit.text()
        graphCategory = dialog.categoryComboBox.currentText()

        if ok and graphName and len(graphName) > 0:
            startNodeName = dialog.startNodeComboBox.currentText()
            self.graphManager.saveGraph(self.graph, graphName, graphCategory, startNodeName=startNodeName)

    def fillListView(self, listView, category):
        items = self.graphManager.graphCategoryToNamesMap.get(category)
        if items == None:
            return

        model = QStandardItemModel()
        listView.setModel(model)

        for item in items:
            sItem = QStandardItem(item)
            model.appendRow(sItem)

    def onLoad(self):
        dialog = self.loadDialog("loadGraphDialog.ui")
        self.setupCategoryComboBox(dialog.categoryComboBox)
        self.fillListView(dialog.graphListView, dialog.categoryComboBox.currentText())
        dialog.categoryComboBox.currentIndexChanged.connect(lambda: self.fillListView(dialog.graphListView, dialog.categoryComboBox.currentText()))

        ok = dialog.exec_()

        if ok:
            selectionModel = dialog.graphListView.selectionModel()
            selectedRows = selectionModel.selectedRows()

            if len(selectedRows) > 0:
                listItem = dialog.graphListView.model().item(selectedRows[0].row())
                graphName = listItem.text()
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
        for n in node_exec.nodes_cfg.NODES_TO_REGISTER:
            self.graph.register_node(n)
        
        self.graph.register_node(BackdropNode)

        self.nodeTree = NodeTreeWidget(node_graph=self.graph)
        self.nodeTree.update()

    def updateNodeRegistration(self):
        for n in node_exec.nodes_cfg.NODES_TO_REGISTER:
            try:
                self.graph.register_node(n)
            except:
                pass

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

    saveDataFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "VisualScripting_SaveData")
    visualScripting = VisualScripting(saveDataFolder)
    visualScripting.window.show()

    app.exec_()
