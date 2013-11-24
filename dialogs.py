from PyQt4.QtGui import *
from PyQt4.QtCore import *

from os.path import splitext, dirname

def saveDialog(parent):
    """Shows a save file dialog and return the selected file path."""
    settings = QSettings()
    key = '/UI/lastShapefileDir'
    outDir = settings.value(key)

    filter = 'Shapefiles (*.shp)'
    outFilePath = QFileDialog.getSaveFileName(parent, parent.tr('Save output shapefile'), outDir, filter)
    outFilePath = unicode(outFilePath)

    if outFilePath:
        root, ext = splitext(outFilePath)
        if ext.upper() != '.SHP':
            outFilePath = '%s.shp' % outFilePath
        outDir = dirname(outFilePath)
        settings.setValue(key, outDir)

    return outFilePath

def openDir(parent):
    settings = QSettings()
    key = '/UI/lastShapefileDir'
    outDir = settings.value(key)

    outPath = QFileDialog.getExistingDirectory(parent, 'Generalizer', outDir)#, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    return outPath
