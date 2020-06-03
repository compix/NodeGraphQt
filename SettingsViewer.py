import os
from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtWidgets import QFileDialog, QMessageBox
from VisualScripting import VisualScripting
from PySide2.QtGui import QStandardItemModel, QStandardItem
from VisualScripting import asset_manager

class SettingsViewer(object):
    def __init__(self, parent, visualScripting : VisualScripting):
        super().__init__()

        self.visualScripting = visualScripting
        self.widget = asset_manager.loadUI("settings.ui")

        self.widget.serializationFolderSelectionButton.clicked.connect(self.onSelectSerializationFolder)
        self.widget.serializationFolderAddButton.clicked.connect(self.onAddSerializationFolder)
        self.widget.serializationFolderDeleteButton.clicked.connect(self.onDeleteSerializationFolder)

        self.serializationFolderListModel = QStandardItemModel()
        self.widget.serializationFolderListView.setModel(self.serializationFolderListModel)

        self.updateSerializationFoldersList()

        self.setupAsDockWidget(parent)

    def updateSerializationFoldersList(self):
        for folder in self.visualScripting.graphManager.serializationFolders:
            self.addSerializationFolderToList(folder)

    def onSelectSerializationFolder(self):
        folder = QFileDialog.getExistingDirectory(self.widget, "Open Directory", self.widget.serializationFolderLineEdit.text())
        self.widget.serializationFolderLineEdit.setText(folder)

    def addSerializationFolderToList(self, folder):
        folderItem = QStandardItem(folder)
        folderItem.setDropEnabled(False)
        self.serializationFolderListModel.appendRow(folderItem)

    def addSerializationFolder(self, folder):
        self.visualScripting.graphManager.addSerializationFolder(folder)
        self.addSerializationFolderToList(folder)

    def onAddSerializationFolder(self):
        folder = self.widget.serializationFolderLineEdit.text()
        try:
            self.addSerializationFolder(folder)
        except Exception as e:
            QMessageBox.warning(self.widget, "Warning", f'Failed to add serialization folder. Reason: {str(e)}')

    def onDeleteSerializationFolder(self):
        try:
            selectionModel = self.widget.serializationFolderListView.selectionModel()
            if len(selectionModel.selectedRows()) > 0:
                if QMessageBox.question(self.widget, "Confirmation", "Are you sure you want to delete the selected serialization folders?") != QMessageBox.Yes:
                    return

            for rowIdx in selectionModel.selectedRows():
                idx = rowIdx.row()
                self.visualScripting.graphManager.removeSerializationFolderByIndex(idx)
                self.serializationFolderListModel.removeRow(idx)
        except Exception as e:
            QMessageBox.warning(self.widget, "Warning", f'Failed to delete folder. Reason: {str(e)}')

    def setupAsDockWidget(self, parent):
        self.dockWidget = QtWidgets.QDockWidget("Visual Scripting Settings", parent)
        self.dockWidget.setWidget(self.widget)
        self.dockWidget.setObjectName("visualScriptingSettingsDockWidget")