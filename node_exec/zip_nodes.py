from node_exec.base_nodes import defNode

from zipfile import ZipFile
import os
from pathlib import Path
import subprocess

IDENTIFIER = "Zip"

pwEncryptionSupported = False
try:
    import pyzipper
    pwEncryptionSupported = True
except:
    print("Note: Password-encryption for zip archives is not supported because the pyzipper module ist missing: pip install pyzipper")

@defNode("Zip Folder", isExecutable=True, returnNames=["Zipped File Path"], identifier=IDENTIFIER)
def zipFolder(folderPath="", outputZipFilePath="", password="", progressHandler=None):
    """
    If a progressHandler is specified, the progress will be updated with 
    progressHandler(progress, currentFileIndex, totalNumberOfFiles) where progress is a float in [0,1].
    """
    relFolder = Path(folderPath).parent
    
    if progressHandler:
        numberOfFiles = sum([len(files) for _, _, files in os.walk(folderPath)])
        progressHandler(0.0, 0, numberOfFiles)
        fileNumber = 0
    
    if password == "" or not pwEncryptionSupported:
        with ZipFile(outputZipFilePath, 'w') as zipFile:
            for folderName, _, filenames in os.walk(folderPath):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipFile.write(filePath, os.path.relpath(filePath, relFolder))

                    if progressHandler:
                        fileNumber += 1
                        progressHandler(float(fileNumber) / numberOfFiles, fileNumber, numberOfFiles)

        return outputZipFilePath
    else:
        with pyzipper.AESZipFile(outputZipFilePath, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zipFile:
            zipFile.pwd = password
            for folderName, _, filenames in os.walk(folderPath):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipFile.write(filePath, os.path.relpath(filePath, relFolder))

                    if progressHandler:
                        fileNumber += 1
                        progressHandler(float(fileNumber) / numberOfFiles, fileNumber, numberOfFiles)

@defNode("Zip Files", isExecutable=True, returnNames=["Zipped File Path"], identifier=IDENTIFIER)
def zipFiles(filePathList=None, outputZipFilePath="", keepRelativeFolderStructure=True, password="", progressHandler=None):
    """
    If a progressHandler is specified, the progress will be updated with 
    progressHandler(progress, currentFileIndex, totalNumberOfFiles) where progress is a float in [0,1].
    """
    if filePathList == None:
        filePathList = []

    # Support single files:
    if not isinstance(filePathList, list):
        filePathList = [filePathList]

    if progressHandler:
        numberOfFiles = len(filePathList)
        progressHandler(0.0, 0, numberOfFiles)
        fileNumber = 0

    relFolder = Path(os.path.commonpath(filePathList)).parent

    if password == "" or not pwEncryptionSupported:
        with ZipFile(outputZipFilePath, 'w') as zipFile:
            for filePath in filePathList:
                if keepRelativeFolderStructure:
                    zipFile.write(filePath, os.path.relpath(filePath, relFolder))
                else:
                    zipFile.write(filePath, os.path.basename(filePath))

                if progressHandler:
                    fileNumber += 1
                    progressHandler(float(fileNumber) / numberOfFiles, fileNumber, numberOfFiles)
    else:
        with pyzipper.AESZipFile(outputZipFilePath, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zipFile:
            zipFile.pwd = password
            for filePath in filePathList:
                if keepRelativeFolderStructure:
                    zipFile.write(filePath, os.path.relpath(filePath, relFolder))
                else:
                    zipFile.write(filePath, os.path.basename(filePath))

                if progressHandler:
                    fileNumber += 1
                    progressHandler(float(fileNumber) / numberOfFiles, fileNumber, numberOfFiles)

    return outputZipFilePath

@defNode("Add Files to Zip", isExecutable=True, returnNames=["Zipped File Path"], identifier=IDENTIFIER)
def addFilesToZip(filePathList=None, existingZipFile="", keepRelativeFolderStructure=True, progressHandler=None):
    """
    If a progressHandler is specified, the progress will be updated with 
    progressHandler(progress, currentFileIndex, totalNumberOfFiles) where progress is a float in [0,1].
    """
    if filePathList == None:
        filePathList = []

    # Support single files:
    if not isinstance(filePathList, list):
        filePathList = [filePathList]

    if progressHandler:
        numberOfFiles = len(filePathList)
        progressHandler(0.0, 0, numberOfFiles)
        fileNumber = 0

    with ZipFile(existingZipFile, 'a') as zipFile:
        relFolder = Path(os.path.commonpath(filePathList)).parent

        for filePath in filePathList:
            if keepRelativeFolderStructure:
                zipFile.write(filePath, os.path.relpath(filePath, relFolder))
            else:
                zipFile.write(filePath, os.path.basename(filePath))

            if progressHandler:
                fileNumber += 1
                progressHandler(float(fileNumber) / numberOfFiles, fileNumber, numberOfFiles)

    return existingZipFile

@defNode("Add Folder to Zip", isExecutable=True, returnNames=["Zipped File Path"], identifier=IDENTIFIER)
def addFolderToZip(folderPath=None, existingZipFile="", progressHandler=None):
    """
    If a progressHandler is specified, the progress will be updated with 
    progressHandler(progress, currentFileIndex, totalNumberOfFiles) where progress is a float in [0,1].
    """
    relFolder = Path(folderPath).parent

    if progressHandler:
        numberOfFiles = sum([len(files) for _, _, files in os.walk(folderPath)])
        progressHandler(0.0, 0, numberOfFiles)
        fileNumber = 0

    with ZipFile(existingZipFile, 'a') as zipFile:
        for folderName, _, filenames in os.walk(folderPath):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipFile.write(filePath, os.path.relpath(filePath, relFolder))

                if progressHandler:
                    fileNumber += 1
                    progressHandler(float(fileNumber) / numberOfFiles, fileNumber, numberOfFiles)
                    
    return existingZipFile

"""
@defNode("Zip", isExecutable=True, returnNames=["Zipped File Path"], identifier=IDENTIFIER)
def make7ZipArchive(filesAndFolders=None, outputZipFilePath="", password=""):
    if filesAndFolders == None:
        filesAndFolders = []

    if not isinstance(filesAndFolders, list):
        filesAndFolders = [filesAndFolders]

    if len(filesAndFolders) > 0:
        pathAdjustedFiles = []
        for f in filesAndFolders:
            pathAdjustedFiles.append(f"\"{os.path.normpath(f)}\"")

        subprocess.call(['7z', 'a', f'-p{password}', '-y', f"\"{os.path.normpath(outputZipFilePath)}\""] + pathAdjustedFiles)
"""