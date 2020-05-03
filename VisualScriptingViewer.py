import os
import sys
import node_exec.nodes_cfg
node_exec.nodes_cfg.init()

from node_exec import *
from node_exec import base_nodes
from node_exec import all_nodes

from NodeGraphQt import (NodeGraph,
                         BaseNode,
                         BackdropNode)
from NodeGraphQt.base import actions
from NodeGraphQt import QtWidgets, QtCore, PropertiesBinWidget, NodeTreeWidget, QtGui
from PySide2 import QtUiTools

from node_exec.GraphManager import GraphManager
import node_exec.NodeGraphQt_mod
from PySide2.QtWidgets import QDialog
from PySide2.QtCore import Qt
from PySide2.QtGui import QStandardItemModel, QStandardItem
from distutils.version import LooseVersion
import subprocess
from core.Event import Event
from core import core
from PySide2.QtCore import QThreadPool
from VisualScripting import VisualScripting
from PySide2.QtWidgets import QMessageBox

class VisualScriptingViewer(object):
    def __init__(self, visualScripting : VisualScripting, parentWindow=None):
        self.graph = NodeGraph()
        self.graphViewer = self.graph.viewer()

        self.graphManager = visualScripting.graphManager

        self.initNodes()
        self.setupPropertiesBin()

        self.window = self.loadUI("graphQt.ui")

        self.splitter =  QtWidgets.QSplitter()
        self.window.bottomLayout.addWidget(self.splitter)
        self.splitter.addWidget(self.nodeTree)
        self.splitter.addWidget(self.graphViewer)
        self.splitter.addWidget(self.propertiesBin)

        self.setupMenuBar(self.graph)

        self.onSaveEvent = Event()

    def onOpenInVisualStudioCode(self):
        QThreadPool.globalInstance().start(core.LambdaTask(self.openInVisualStudioCode))
        
    def openInVisualStudioCode(self):
        session = self.graphManager.curSession
        if session != None:
            codePath = self.graphManager.getPythonCodePath(session.graphSettings)

            try:
                subprocess.Popen(f'code \"{os.path.normpath(codePath)}\"', shell=True)
            except Exception as e:
                print(f"Failed: {e} - Please make sure Visual Studio Code is installed and 'code' is registered as a command.")

    def loadUI(self, relUIPath):
        uiFilePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), relUIPath)
        uiFile = QtCore.QFile(uiFilePath)
        uiFile.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        return loader.load(uiFile)

    # Modified setup_context_menu from NodeGraphQt.base.actions
    def setupMenuBar(self, graph : NodeGraph):
        rootMenu = graph.context_menu()

        fileMenu = rootMenu.add_menu('&File')
        editMenu = rootMenu.add_menu('&Edit')

        # create "File" menu.
        fileMenu.add_command('Open Graph...',
                            lambda: actions._open_session(graph),
                            QtGui.QKeySequence.Open)
        fileMenu.add_command('Export Graph As...',
                            lambda: actions._save_session_as(graph),
                            'Alt+Shift+s')
        fileMenu.add_command('Clear', lambda: actions._clear_session(graph))

        fileMenu.add_separator()

        fileMenu.add_command('Zoom In', lambda: actions._zoom_in(graph), '=')
        fileMenu.add_command('Zoom Out', lambda: actions._zoom_out(graph), '-')
        fileMenu.add_command('Reset Zoom', graph.reset_zoom, 'h')

        # create "Edit" menu.
        undo_actn = graph.undo_stack().createUndoAction(graph.viewer(), '&Undo')
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            undo_actn.setShortcutVisibleInContextMenu(True)
        undo_actn.setShortcuts(QtGui.QKeySequence.Undo)
        editMenu.qmenu.addAction(undo_actn)

        redo_actn = graph.undo_stack().createRedoAction(graph.viewer(), '&Redo')
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            redo_actn.setShortcutVisibleInContextMenu(True)
        redo_actn.setShortcuts(QtGui.QKeySequence.Redo)
        editMenu.qmenu.addAction(redo_actn)

        editMenu.add_separator()
        editMenu.add_command('Clear Undo History', lambda: actions._clear_undo(graph))
        editMenu.add_separator()

        editMenu.add_command('Copy', graph.copy_nodes, QtGui.QKeySequence.Copy)
        editMenu.add_command('Paste', graph.paste_nodes, QtGui.QKeySequence.Paste)
        editMenu.add_command('Delete',
                            lambda: graph.delete_nodes(graph.selected_nodes()),
                            QtGui.QKeySequence.Delete)

        editMenu.add_separator()

        editMenu.add_command('Select all', graph.select_all, 'Ctrl+A')
        editMenu.add_command('Deselect all', graph.clear_selection, 'Ctrl+Shift+A')
        editMenu.add_command('Enable/Disable',
                            lambda: graph.disable_nodes(graph.selected_nodes()),
                            'd')

        editMenu.add_command('Duplicate',
                            lambda: graph.duplicate_nodes(graph.selected_nodes()),
                            'Alt+c')
        editMenu.add_command('Center Selection',
                            graph.fit_to_selection,
                            'f')

        editMenu.add_separator()

        menuBar = QtWidgets.QMenuBar()
        sessionMenu = QtWidgets.QMenu("Session")

        menuBar.addMenu(fileMenu.qmenu)
        menuBar.addMenu(editMenu.qmenu)
        menuBar.addMenu(sessionMenu)
        menuBar.setMaximumHeight(20)

        self.saveAction = QtWidgets.QAction("Save")
        self.saveAction.setShortcut(QtGui.QKeySequence.Save)
        self.saveAction.triggered.connect(self.onSave)

        self.saveAsAction = QtWidgets.QAction("Save As...")
        self.saveAsAction.setShortcut("Ctrl+Shift+S")
        self.saveAsAction.triggered.connect(self.onSaveAs)

        self.loadAction = QtWidgets.QAction("Load")
        self.loadAction.triggered.connect(self.onLoad)

        self.runAction = QtWidgets.QAction("Run")
        self.runAction.triggered.connect(self.onRun)
        self.runAction.setShortcut(QtGui.QKeySequence("R"))

        self.openInCode = QtWidgets.QAction("Show Code In Visual Studio Code")
        self.openInCode.triggered.connect(self.onOpenInVisualStudioCode)
        self.openInCode.setShortcut(QtGui.QKeySequence("Q"))

        sessionMenu.addAction(self.saveAction)
        sessionMenu.addAction(self.saveAsAction)
        sessionMenu.addAction(self.loadAction)
        sessionMenu.addAction(self.runAction)
        sessionMenu.addAction(self.openInCode)

        self.window.verticalLayout.insertWidget(0, menuBar)

    def onRun(self):
        if self.graphManager.curSession != None:
            self.graphManager.executeGraph()
        else:
            QMessageBox.critical(None, "Unsaved state", "Please save the graph first.")
        
    def setupCategoryComboBox(self, comboBox):
        categories = self.graphManager.graphCategoryToNamesMap.keys()
        for category in categories:
            comboBox.addItem(category)

    def loadDialog(self, relUIPath) -> QDialog:
        dialog = self.loadUI(relUIPath)
        dialog.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        return dialog

    def saveAs(self):
        currentGraphName = self.graphManager.getSessionGraphName()
        currentStartNodeName = self.graphManager.getSessionStartNodeName()
        currentCategory = self.graphManager.getSessionCategory()

        dialog = self.loadDialog("saveGraphDialog.ui")
        dialog.graphNameLineEdit.setText(currentGraphName)
        self.setupCategoryComboBox(dialog.categoryComboBox)

        dialog.categoryComboBox.setCurrentText(currentCategory)

        scriptingNodes = [n for n in self.graph.all_nodes() if n.isScriptingNode]
        allGraphNodeNames = [n.name() for n in scriptingNodes if n.isViableStartNode]
        for n in allGraphNodeNames:
            dialog.startNodeComboBox.addItem(n)
        
        if currentStartNodeName in allGraphNodeNames:
            dialog.startNodeComboBox.setCurrentText(currentStartNodeName)

        ok = dialog.exec_()
        graphName = dialog.graphNameLineEdit.text()
        graphCategory = dialog.categoryComboBox.currentText()

        if ok and graphName and len(graphName) > 0:
            startNodeName = dialog.startNodeComboBox.currentText()

            writeGraph = True
            if self.graphManager.doesGraphExist(graphName, graphCategory, startNodeName):
                ret = QMessageBox.question(None, "Name already exists.", "Are you sure you want to overwrite the existing graph with the same name?")
                writeGraph = ret == QMessageBox.Yes

            if writeGraph:
                self.graphManager.saveGraph(self.graph, graphName, graphCategory, startNodeName=startNodeName)

        self.onSaveEvent()

    def onSave(self):
        if self.graphManager.curSession != None:
            self.graphManager.saveCurrentSession()
            self.onSaveEvent()
            return

        self.saveAs()

    def onSaveAs(self):
        self.saveAs()

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
                category = dialog.categoryComboBox.currentText()
                self.graphManager.loadGraph(self.graph, graphName, category)

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
    visualScriptingViewer = VisualScriptingViewer(visualScripting)
    visualScriptingViewer.window.show()

    app.exec_()
