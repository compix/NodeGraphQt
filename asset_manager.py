from os import path
import os
from datetime import datetime
from PySide2 import QtCore, QtUiTools

BASE_PATH = path.join(path.dirname(path.realpath(__file__)), "assets")
BASE_UI_FILES_PATH = path.join(BASE_PATH, "ui_files")

def getUIFilePath(uiFileName):
    return path.join(BASE_UI_FILES_PATH, uiFileName)

def getMainSettingsPath():
    return path.join(BASE_PATH, "settings.ini")

def getLogFilePath():
    curDateAndTime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    logFilename = f"{curDateAndTime}.log"

    return path.abspath(path.join("log_output", logFilename))

def loadUI(relUIPath):
    uiFilePath = os.path.join(BASE_UI_FILES_PATH, relUIPath)
    uiFile = QtCore.QFile(uiFilePath)
    uiFile.open(QtCore.QFile.ReadOnly)
    loader = QtUiTools.QUiLoader()
    return loader.load(uiFile)