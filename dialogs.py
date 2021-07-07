from builtins import str
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from  PyQt5.QtWidgets import *

from os.path import splitext, dirname

def saveDialog(parent):
    """Shows a save file dialog and return the selected file path."""
    settings = QSettings()
    key = '/UI/lastShapefileDir'
    outDir = settings.value(key)

    filter = 'GeoPackage (*.gpkg)'
    outFilePath, __ = QFileDialog.getSaveFileName(parent, parent.tr('Save output GeoPackage'), outDir, filter)
    outFilePath = str(outFilePath)

    if outFilePath:
        root, ext = splitext(outFilePath)
        if ext.upper() != '.GPKG':
            outFilePath = '%s.gpkg' % outFilePath
        outDir = dirname(outFilePath)
        settings.setValue(key, outDir)

    return outFilePath

def openDir(parent):
    settings = QSettings()
    key = '/UI/lastShapefileDir'
    outDir = settings.value(key)

    outPath = QFileDialog.getExistingDirectory(parent, 'Generalizer', outDir)#, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    return outPath
