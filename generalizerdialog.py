"""
/***************************************************************************
 generalizerDialog
                                 A QGIS plugin
 Lines generalization (smooth and simplify) based on v.generalize GRASS module
                             -------------------
        begin                : 2011-08-17
        copyright            : (C) 2011 by Piotr Pociask
        email                : ppociask (at) o2 pl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from os.path import splitext, dirname


import smooth, simplify, points

from ui_generalizer import Ui_generalizer
# create the dialog for zoom to point
class generalizerDialog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_generalizer()
        self.ui.setupUi(self)
        self.iface = iface

        QObject.connect( self.ui.bBrowse, SIGNAL( "clicked()" ), self.outFile )
        QObject.connect( self.ui.bOk, SIGNAL( "clicked()" ), self.generalize )
        QObject.connect( self.ui.cbAlgorithm, SIGNAL( "currentIndexChanged(int)" ), self.cbChange )
        QObject.connect( self.ui.bHelp, SIGNAL( "clicked()" ), self.showHelp )

        layerList = getLayersNames()
        self.ui.cbInput.addItems(layerList)

    def showHelp(self):
        QMessageBox.question(self, 'Generalizer', """Generalizer \n
Version 0.1 \n
p0cisk (at) o2 (dot) pl""")

    def outFile(self):
        """Open a file save dialog and set the output file path."""
        outFilePath = saveDialog(self)
        if not outFilePath:
            return
        self.ui.eOutput.setText(QString(outFilePath))

    def cbChange(self, index):
        if index == 0: self.ui.cbAlgorithm.setCurrentIndex(1)
        elif index == 1: self.ui.stackOptions.setCurrentIndex(index-1) #generalization
        elif index == 2: self.ui.cbAlgorithm.setCurrentIndex(3)
        elif index < 6: self.ui.stackOptions.setCurrentIndex(index-2) #simplify
        elif index == 6: self.ui.cbAlgorithm.setCurrentIndex(7)
        else: self.ui.stackOptions.setCurrentIndex(index-3) #smooth


    def GetArguments(self):
        arguments = {}
        arguments['remove_thresh'] = self.ui.sbRemove_thresh.value()
        arguments['dp_thresh'] = self.ui.sbDP_thresh.value()
        arguments['lang_thresh'] = self.ui.sbLang_thresh.value()
        arguments['lang_LA'] = self.ui.sbLang_LA.value()
        arguments['reduction_thresh'] = self.ui.sbReduction_thresh.value()
        arguments['boyle_LA'] = self.ui.sbBoyle_LA.value()
        arguments['slide_slide'] = self.ui.sbSlide_slide.value()
        arguments['slide_LA'] = self.ui.sbSlide_LA.value()
        arguments['dist_slide'] = self.ui.sbDist_slide.value()
        arguments['dist_LA'] = self.ui.sbDist_LA.value()
        arguments['chaiken_level'] = self.ui.sbChaiken_level.value()
        arguments['chaiken_weight'] = self.ui.sbChaiken_weight.value()

        return arguments

    def GetFunction(self, arguments):
        if self.ui.cbAlgorithm.currentText() == 'Boyle\'s Forward-Looking Algorithm':
            return self.boyle
        elif self.ui.cbAlgorithm.currentText() == 'McMaster\'s Sliding Averaging Algorithm':
            if arguments['slide_LA']%2 == 0:
                QMessageBox.critical(None, 'Generalizer', 'Look ehead parameter must be odd number!')
                return None
            else:
                return self.sliding_averaging
        elif self.ui.cbAlgorithm.currentText() == 'McMaster\'s Distance-Weighting Algorithm':
            if arguments['dist_LA']%2 == 0:
                QMessageBox.critical(None, 'Generalizer', 'Look ehead parameter must be odd number!')
                return None
            else:
                return self.distance_weighting
        elif self.ui.cbAlgorithm.currentText() == 'Chaiken\'s Algorithm':
            return self.chaiken
        elif self.ui.cbAlgorithm.currentText() == 'Vertex Reduction':
            return self.vertex_reduction
        elif self.ui.cbAlgorithm.currentText() == 'Douglas-Peucker Algorithm':
            return self.douglas_pecker
        elif self.ui.cbAlgorithm.currentText() == 'Remove small objects':
            return self.remove
        elif self.ui.cbAlgorithm.currentText() == 'Lang Algorithm':
            return self.lang

    def LoadLayer(self, path):
        msg = QMessageBox.question(self, 'Generalizer', 'New layer created. \n Add to TOC?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            if path.contains("\\"):
                out_name = path.right((path.length() - path.lastIndexOf("\\")) - 1)
            else:
                out_name = path.right((path.length() - path.lastIndexOf("/")) - 1)

            if out_name.endsWith(".shp"):
                out_name = out_name.left(out_name.length() - 4)

                self.iface.addVectorLayer(path, out_name, "ogr")


    def generalize(self):
        if self.ui.eOutput.text() == '':
            QMessageBox.critical(None, 'Generalizer', 'Enter output file name!')
            return
        if self.ui.cbInput.currentText() == '':
            QMessageBox.critical(None, 'Generalizer', 'No line layers!')
            return

        arguments = self.GetArguments()

        func = self.GetFunction(arguments)
        if func == None:
            return


        ilayer = getMapLayerByName(self.ui.cbInput.currentText())
        iprovider = ilayer.dataProvider()
        allAttrs = iprovider.attributeIndexes()
        fields = iprovider.fields()

        feat = QgsFeature()
        iprovider.select(allAttrs)
        fet = QgsFeature()


        writer = QgsVectorFileWriter(self.ui.eOutput.text(), iprovider.encoding(), fields, QGis.WKBLineString, ilayer.srs())
        if writer.hasError() != QgsVectorFileWriter.NoError:
            QMessageBox.critical(None, 'Generalizer', 'Error when creating shapefile: %s' % (writer.hasError()))
            #print "Error when creating shapefile: ", writer.hasError()

        while iprovider.nextFeature(feat):
            geom = feat.geometry()
            if geom.isMultipart():
                lm = geom.asMultiPolyline()
                l = []
                for ls in lm:
                    p = func(ls, **arguments)
                    l2 = []
                    for n in range(p.n_points):
                        l2.append(QgsPoint(p.x[n], p.y[n]))
                    if len(l2) != 0:
                        l.append(l2)
                if len(l) != 0:
                    fet.setGeometry(QgsGeometry.fromMultiPolyline(l))
            else:
                ls = geom.asPolyline()
                p = func(ls, **arguments)
                l = []
                for n in range(p.n_points):
                    l.append(QgsPoint(p.x[n], p.y[n]))

                if len(l) != 0:
                    fet.setGeometry(QgsGeometry.fromPolyline(l))
            fet.setAttributeMap(feat.attributeMap())
            writer.addFeature(fet)

        del writer
        #self.iface.addVectorLayer("C:\Documents and Settings\Pocisk\Pulpit\my_shapes.shp", "boyle_", "ogr")
        self.LoadLayer(self.ui.eOutput.text())

        self.close()

    def remove(self, l, **kwargs):
        #Vertex Remove Algorithm
        thresh = kwargs['remove_thresh']
        length = 0.
        p = points.Vect_new_line_struct(l)
        p1 = points.point()
        p2 = points.point()

        for i in range(p.n_points-1):
            points.point_assign(p, i, p1)
            points.point_assign(p, i+1, p2)
            length = length + points.point_dist(p1, p2)

        #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str( length ) )
        if length < thresh:
            p.x = []
            p.y = []
            p.n_points = 0

        return p

    def boyle(self,l,  **kwargs):
        #Boyle's Forward-Looking Algorithm
        p = points.Vect_new_line_struct(l)
        n = smooth.boyle(p, kwargs['boyle_LA'])

        return p

    def sliding_averaging(self,l,  **kwargs):
        #McMaster's Sliding Averaging Algorithm
        p = points.Vect_new_line_struct(l)
        n = smooth.sliding_averaging(p, kwargs['slide_slide'], kwargs['slide_LA'])

        return p

    def distance_weighting(self,l,  **kwargs):
        #McMaster's Distance Weighting Algorithm
        p = points.Vect_new_line_struct(l)
        n = smooth.distance_weighting(p, kwargs['dist_slide'], kwargs['dist_LA'])

        return p

    def chaiken(self,l,  **kwargs):
        #Chaiken's Algorithm
        p = points.Vect_new_line_struct(l)
        n = smooth.chaiken(p, kwargs['chaiken_level'], kwargs['chaiken_weight'])

        return p

    def vertex_reduction(self,l,  **kwargs):
        #Vertex Reduction
        #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(l) )
        p = points.Vect_new_line_struct(l)
        n = simplify.vertex_reduction(p, kwargs['reduction_thresh'])

        return p

    def douglas_pecker(self,l,  **kwargs):
        #Douglas-Pecker Algorithm
        tmp = simplify.douglas_pecker(l, kwargs['dp_thresh'])
        p = points.Vect_new_line_struct(tmp)

        return p

    def lang(self,l,  **kwargs):
        #Vertex Reduction
        #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str( l ) )
        p = points.Vect_new_line_struct(l)
        n = simplify.lang(p, kwargs['lang_thresh'], kwargs['lang_LA'])

        return p


def getLayersNames():
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    layerlist = []
    for name, layer in layermap.iteritems():
        if layer.type() == QgsMapLayer.VectorLayer:
            if layer.geometryType() == QGis.Line:
                layerlist.append( unicode( layer.name() ) )

    return layerlist

def getMapLayerByName(myName ):
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layermap.iteritems():
        if layer.name() == myName:
            if layer.isValid():
                return layer
            else:
                return None

def saveDialog(parent):
  """Shows a save file dialog and return the selected file path."""
  settings = QSettings()
  key = '/UI/lastShapefileDir'
  outDir = settings.value(key).toString()
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