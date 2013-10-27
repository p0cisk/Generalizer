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

import smooth, simplify, points
from dialogs import *

from ui_generalizer import Ui_generalizer

#global variable with short to full algorithm names
algorithm  = {'remove':'Remove small objects',
              'DP':'Douglas-Peucker Algorithm',
              'lang':'Lang Algorithm',
              'reduction':'Vertex Reduction',
              'boyle':'Boyle\'s Forward-Looking Algorithm',
              'chaiken':'Chaiken\'s Algorithm',
              'hermite':'Hermite Spline Interpolation',
              'distance':'McMaster\'s Distance-Weighting Algorithm',
              'sliding':'McMaster\'s Sliding Averaging Algorithm',
              'snakes':'Snakes Algorithm',
              'jenks':'Jenk\'s Algorithm',
              'RW':'Reumann-Witkam Algorithm'
              }


class generalizerDialog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_generalizer()
        self.ui.setupUi(self)
        self.iface = iface

        self.ui.sbJenks_angle.setVisible(False)
        self.ui.label_8.setVisible(False)

        #set signals
        QObject.connect( self.ui.bBrowse, SIGNAL( "clicked()" ), self.outFile )
        QObject.connect( self.ui.bBrowseDir, SIGNAL( "clicked()" ), self.outDir )
        QObject.connect( self.ui.bOk, SIGNAL( "clicked()" ), self.generalize )
        QObject.connect( self.ui.cbAlgorithm, SIGNAL( "currentIndexChanged(int)" ), self.cbChange )
        QObject.connect( self.ui.bHelp, SIGNAL( "clicked()" ), self.showHelp )
        QObject.connect( self.ui.cbBatch, SIGNAL( "stateChanged(int)" ), self.BatchOn )
        QObject.connect( self.ui.bAddAlg, SIGNAL( "clicked()" ), self.AddAlgorithm )
        QObject.connect( self.ui.bDelAlg, SIGNAL( "clicked()" ), self.DelAlgorithm )
        QObject.connect( self.ui.bEditAlg, SIGNAL( "clicked()" ), self.EditAlgorithm )
        QObject.connect( self.ui.cbOutFile, SIGNAL( "stateChanged(int)" ), self.FileEnabled )
        QObject.connect( self.ui.cbOutDir, SIGNAL( "stateChanged(int)" ), self.DirEnabled )

        #load line layers to lists
        self.layerList = getLayersNames()
        self.ui.cbInput.addItems(self.layerList)
        self.ui.lstLayers.addItems(self.layerList)
        [self.ui.lstLayers.item(i).setCheckState(Qt.Unchecked) for i in range(self.ui.lstLayers.count()) ]

    def FileEnabled(self, state):
        #enable or disable path to file
        enabled = self.ui.eOutput.isEnabled()
        self.ui.eOutput.setEnabled(not enabled)
        self.ui.bBrowse.setEnabled(not enabled)

    def DirEnabled(self, state):
        #enable/disable directory
        enabled = self.ui.eDir.isEnabled()
        self.ui.eDir.setEnabled(not enabled)
        self.ui.bBrowseDir.setEnabled(not enabled)

    def AddAlgorithm(self):
        #add new algorithm in batch mode
        self.doAddAlgorithm(self.ui.tblBatchAlg.rowCount())

    def EditAlgorithm(self):
        #edit algorithm in batch mode
        if self.ui.tblBatchAlg.currentRow() == -1:
            QMessageBox.warning(self, 'Generalizer', 'Select algorithm to edit!')
            return

        self.doAddAlgorithm(self.ui.tblBatchAlg.currentRow())

    def doAddAlgorithm(self, index):
        #add new algorithm in batch mode
        global algorithm

        new = index > self.ui.tblBatchAlg.rowCount()-1

        items = QStringList( [self.ui.cbAlgorithm.itemText(i) for i in range(self.ui.cbAlgorithm.count())] )
        algName = QInputDialog.getItem(None, 'Generalizer', 'Choose algorithm:', items, 1, False)
        if not algName[1] or algName[0].left(1) == '-': return
        #QMessageBox.question(self, 'Generalizer', str(alg))
        par1 = None
        par2 = None

        if algName[0] == algorithm['boyle']:#Boyle\'s Forward-Looking Algorithm':
            par1 = QSpinBox()
            par1.setRange(2, 999)
            msg = QInputDialog.getInt(None, 'Generalizer', 'Look ahead:', 7, 2)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Look ahead')

        elif algName[0] == algorithm['sliding']:#'McMaster\'s Sliding Averaging Algorithm':
            par1 = QDoubleSpinBox()
            par1.setDecimals(2)
            par1.setRange(0, 99.99)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Slide:', 0.5, 0, 99.99)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Slide')

            par2 = QSpinBox()
            par2.setRange(3, 999)
            par2.setSingleStep(2)
            par2.setValue(6)
            while par2.value()%2 == 0:
                msg = QInputDialog.getInt(None, 'Generalizer', 'Look ahead (must be odd number):', par2.value()+1, 3, 999)
                if not msg[1]: return
                par2.setValue(msg[0])
                par2.setToolTip('Look ahead')


        elif algName[0] == algorithm['distance']:#'McMaster\'s Distance-Weighting Algorithm':
            par1 = QDoubleSpinBox()
            par1.setDecimals(2)
            par1.setRange(0, 99.99)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Slide:', 0.5, 0, 99.99)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Slide')

            par2 = QSpinBox()
            par2.setRange(3, 999)
            par2.setSingleStep(2)
            par2.setValue(6)
            while par2.value()%2 == 0:
                msg = QInputDialog.getInt(None, 'Generalizer', 'Look ahead (must be odd number):', par2.value()+1, 3, 999)
                if not msg[1]: return
                par2.setValue(msg[0])
                par2.setToolTip('Look ahead')

        elif algName[0] == algorithm['chaiken']: #'Chaiken\'s Algorithm':
            par1 = QSpinBox()
            par1.setRange(0, 99)
            msg = QInputDialog.getInt(None, 'Generalizer', 'Level:', 1, 0, 99)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Level')

            par2 = QDoubleSpinBox()
            par2.setDecimals(2)
            par2.setRange(1, 99.99)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Weight:', 3., 1, 99.99)
            if not msg[1]: return
            par2.setValue(msg[0])
            par2.setToolTip('Weight')

        elif algName[0] == algorithm['reduction']:#'Vertex Reduction':
            par1 = QDoubleSpinBox()
            par1.setDecimals(4)
            par1.setRange(0.0001, 9999999.9999)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Threshold:', 0.0001, 0.0001, 9999999.9999, 4)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Threshold')

        elif algName[0] == algorithm['DP']:#'Douglas-Peucker Algorithm':
            par1 = QDoubleSpinBox()
            par1.setDecimals(4)
            par1.setRange(0.0001, 9999999.9999)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Threshold:', 0.0001, 0.0001, 9999999.9999, 4)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Threshold')

        elif algName[0] == algorithm['remove']:#'Remove small objects':
            par1 = QDoubleSpinBox()
            par1.setDecimals(4)
            par1.setRange(0.0001, 9999999.9999)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Threshold:', 0.0001, 0.0001, 9999999.9999, 4)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Threshold')

        elif algName[0] == algorithm['lang']:#'Lang Algorithm':
            par1 = QDoubleSpinBox()
            par1.setDecimals(2)
            par1.setRange(0.0001, 9999999.9999)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Threshold:', 0.0001, 0.0001, 9999999.9999, 4)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Threshold')

            par2 = QSpinBox()
            par2.setRange(1, 9999)
            msg = QInputDialog.getInt(None, 'Generalizer', 'Look ahead:', 8, 1, 999)
            if not msg[1]: return
            par2.setValue(msg[0])
            par2.setToolTip('Look ahead')


        elif algName[0] == algorithm['hermite']:#'Hermite Spline Interpolation':
            par1 = QDoubleSpinBox()
            par1.setDecimals(4)
            par1.setRange(0.0001, 9999999.9999)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Threshold:', 2., 0.0001, 9999999.9999, 4)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Threshold')

            par2 = QDoubleSpinBox()
            par2.setDecimals(2)
            par2.setRange(0, 1)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Thightness:', 0.5, 0, 1, 2)
            if not msg[1]: return
            par2.setValue(msg[0])
            par2.setToolTip('Thightness')

        elif algName[0] == algorithm['snakes']:#'Snakes algorithm':
            par1 = QDoubleSpinBox()
            par1.setDecimals(2)
            par1.setRange(0, 9999.99)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Alpha:', 1., 0.00, 9999.99, 2)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Alpha')

            par2 = QDoubleSpinBox()
            par2.setDecimals(2)
            par2.setRange(0, 9999.99)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Beta:', 0.5, 0., 9999.99, 2)
            if not msg[1]: return
            par2.setValue(msg[0])
            par2.setToolTip('Beta')

        elif algName[0] == algorithm['jenks']:#'Snakes algorithm':
            par1 = QDoubleSpinBox()
            par1.setDecimals(4)
            par1.setRange(0, 9999999.9999)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Threshold:', 0.0001, 0.00, 9999999.9999, 4)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Threshold')

            """par2 = QDoubleSpinBox()
            par2.setRange(0, 180)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Angle threshold:', 3, 0., 180, 2)
            if not msg[1]: return
            par2.setValue(msg[0])
            par2.setToolTip('Angle threshold') """

        elif algName[0] == algorithm['RW']:#Reumann-Witkam Algorithm
            par1 = QDoubleSpinBox()
            par1.setDecimals(4)
            par1.setRange(0, 9999999.9999)
            msg = QInputDialog.getDouble(None, 'Generalizer', 'Threshold:', 0.0001, 0.00, 9999999.9999, 4)
            if not msg[1]: return
            par1.setValue(msg[0])
            par1.setToolTip('Threshold')

        #QMessageBox.question(self, 'Generalizer', str(type(par1)))
        itemAlg = QTableWidgetItem(algName[0])
        itemAlg.setFlags(Qt.ItemIsEnabled)

        if new:
            self.ui.tblBatchAlg.setRowCount(self.ui.tblBatchAlg.rowCount()+1)

        self.ui.tblBatchAlg.setItem(index, 0, itemAlg)
        self.ui.tblBatchAlg.setCellWidget(index, 1, par1)
        if par2 == None:
            self.ui.tblBatchAlg.setCellWidget(index, 2, None)
            par2 = QTableWidgetItem(0)
            par2.setFlags(Qt.ItemIsSelectable)
            self.ui.tblBatchAlg.setItem(index, 2, par2)
        else:
            self.ui.tblBatchAlg.setCellWidget(index, 2, par2)

    def DelAlgorithm(self):
        #del algorithm in batch mode
        if self.ui.tblBatchAlg.currentRow() == -1:
            QMessageBox.warning(self, 'Generalizer', 'Select algorithm to delete!')
            return

        alg = self.ui.tblBatchAlg.item(self.ui.tblBatchAlg.currentRow(), 0).text()
        msg = QMessageBox.question(self, 'Generalizer', 'Do you want to delete %s' % (alg), QMessageBox.Yes | QMessageBox.No)

        if msg == QMessageBox.Yes:
            self.ui.tblBatchAlg.removeRow(self.ui.tblBatchAlg.currentRow())

    def BatchOn(self, state):
        #set batch mode on/off
        if state == 0:
            self.ui.stackBatch.setCurrentIndex(0)
        else:
            self.ui.stackBatch.setCurrentIndex(1)

    def showHelp(self):
        #show information about plugin
        QMessageBox.information(self, 'Generalizer', """Generalizer
Version 0.3

Created by
Piotr Pociask

This plugin is marked as experimental.
If you find any bugs or have suggestions,
please contact with me:
opengis84 (at) gmail (dot) com

""")

    def outFile(self):
        """Open a file save dialog and set the output file path."""
        outFilePath = saveDialog(self)
        if not outFilePath:
            return
        self.ui.eOutput.setText(QString(outFilePath))

    def outDir(self):
        #select directory to save layer(s) in created batch mode
        outPath = openDir(self)
        if outPath:
            self.ui.eDir.setText(outPath)

    def cbChange(self, index):
        #set parameters after algorithm change
        if index == 0: self.ui.cbAlgorithm.setCurrentIndex(1)
        elif index == 1: self.ui.stackOptions.setCurrentIndex(index-1) #generalization
        elif index == 2: self.ui.cbAlgorithm.setCurrentIndex(3)
        elif index < 8: self.ui.stackOptions.setCurrentIndex(index-2) #simplify
        elif index == 8: self.ui.cbAlgorithm.setCurrentIndex(9)
        else: self.ui.stackOptions.setCurrentIndex(index-3) #smooth


    def GetArguments(self, par1=-1, par2=-1):
        #set parameters to algorithm
        if not self.ui.cbBatch.checkState():
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
            arguments['hermite_thresh'] = self.ui.sbHermite_steps.value()
            arguments['hermite_tightness'] = self.ui.sbHermite_tightness.value()
            arguments['jenks_thresh'] = self.ui.sbJenks_thresh.value()
            arguments['jenks_angle'] = self.ui.sbJenks_angle.value()
            arguments['snakes_alpha'] = self.ui.sbSnakes_alpha.value()
            arguments['snakes_beta'] = self.ui.sbSnakes_beta.value()
            arguments['rw_thresh'] = self.ui.sbRW_thresh.value()
        else:
            arguments = {}
            arguments['remove_thresh'] = par1
            arguments['dp_thresh'] = par1
            arguments['lang_thresh'] = par1
            arguments['lang_LA'] = par2
            arguments['reduction_thresh'] = par1
            arguments['boyle_LA'] = par1
            arguments['slide_slide'] = par1
            arguments['slide_LA'] = par2
            arguments['dist_slide'] = par1
            arguments['dist_LA'] = par2
            arguments['chaiken_level'] = par1
            arguments['chaiken_weight'] = par2
            arguments['hermite_thresh'] = par1
            arguments['hermite_tightness'] = par2
            arguments['jenks_thresh'] = par1
            arguments['jenks_angle'] = par2
            arguments['snakes_alpha'] = par1
            arguments['snakes_beta'] = par2
            arguments['rw_thresh'] = par1

        if (arguments['slide_LA']%2 == 0) or (arguments['dist_LA']%2 == 0):
            QMessageBox.critical(None, 'Generalizer', 'Look ehead parameter must be odd number!')
            return None
        else:
            return arguments

    def GetFunction(self, funcName):
        #set function from name
        global algorithm

        if funcName == algorithm['boyle']:#'Boyle\'s Forward-Looking Algorithm':
            return self.boyle
        elif funcName == algorithm['sliding']:#'McMaster\'s Sliding Averaging Algorithm':
            return self.sliding_averaging
        elif funcName == algorithm['distance']:#'McMaster\'s Distance-Weighting Algorithm':
            return self.distance_weighting
        elif funcName == algorithm['chaiken']:#'Chaiken\'s Algorithm':
            return self.chaiken
        elif funcName == algorithm['reduction']:#'Vertex Reduction':
            return self.vertex_reduction
        elif funcName == algorithm['DP']:#'Douglas-Peucker Algorithm':
            return self.douglas_peucker
        elif funcName == algorithm['remove']:#'Remove small objects':
            return self.remove
        elif funcName == algorithm['lang']:#'Lang Algorithm':
            return self.lang
        elif funcName == algorithm['hermite']:#'Hermite Spline Interpolation':
            return self.hermite
        elif funcName == algorithm['jenks']:#'Jenk's Algorithm':
            return self.jenks
        elif funcName == algorithm['snakes']:#'Snakes':
            return self.snakes
        elif funcName == algorithm['RW']:#'Reumann-Witkam Algorithm':
            return self.reumann_witkam

    def NameFromFunc(self, func, arguments):
        if func == self.boyle:
            return '-boyle_LA-' + str(arguments['boyle_LA'])
        elif func == self.sliding_averaging:
            return '-slide_slide-' + str(arguments['slide_slide']) + '_LA-' + str(arguments['slide_LA'])
        elif func == self.distance_weighting:
            return '-dist_slide-' + str(arguments['dist_slide']) + '_LA-' + str(arguments['dist_LA'])
        elif func == self.chaiken:
            return '-chaiken_level-' + str(arguments['chaiken_level']) + '_weight-' + str(arguments['chaiken_weight'])
        elif func == self.vertex_reduction:
            return '-reduction_thresh-' + str(arguments['reduction_thresh'])
        elif func == self.douglas_peucker:
            return '-DP_thresh-' + str(arguments['dp_thresh'])
        elif func == self.remove:
            return '-remove_thresh-' + str(arguments['remove_thresh'])
        elif func == self.lang:
            return '-lang_thresh-' + str(arguments['lang_thresh']) + '_LA-' + str(arguments['lang_LA'])
        elif func == self.hermite:
            return '-hermite_thresh-' + str(arguments['hermite_thresh']) + '_tight-' + str(arguments['hermite_tightness'])
        elif func == self.jenks:
            return '-jenks_thresh-' + str(arguments['jenks_thresh']) + '_angle-' + str(arguments['jenks_angle'])
        elif func == self.snakes:
            return '-snakes_alpha-' + str(arguments['snakes_alpha']) + '_beta-' + str(arguments['snakes_beta'])
        elif func == self.reumann_witkam:
            return '-RW_thresh-' + str(arguments['rw_thresh'])


    def LoadLayers(self, fileList):
        #load created layer
        msg = QMessageBox.question(self, 'Generalizer', 'New layer(s) created. \n Add to TOC?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            for filePath in fileList:
                if filePath.contains("\\"):
                    out_name = filePath.right((filePath.length() - filePath.lastIndexOf("\\")) - 1)
                else:
                    out_name = filePath.right((filePath.length() - filePath.lastIndexOf("/")) - 1)

                if out_name.endsWith(".shp"):
                    out_name = out_name.left(out_name.length() - 4)

                    self.iface.addVectorLayer(filePath, out_name, "ogr")


    def doGeneralize(self, iLayerName, iLayer, oPath, func, arguments):
        #do calculations
        feat = QgsFeature()
        fet = QgsFeature()

        iProvider = iLayer.dataProvider()
        allAttrs = iProvider.attributeIndexes()
        fields = iProvider.fields()
        iProvider.select(allAttrs)

        if oPath == 'memory': #create memory layer
            if iLayer.wkbType() == QGis.WKBLineString:
                mLayer = QgsVectorLayer('LineString', iLayerName + '_memory', 'memory')#self.NameFromFunc(func, arguments), 'memory')
            else:
                mLayer = QgsVectorLayer('MultiLineString', iLayerName + '_memory', 'memory')#self.NameFromFunc(func, arguments), 'memory')

            mProvider = mLayer.dataProvider()
            mProvider.addAttributes( [fields[key] for key in fields] )

            while iProvider.nextFeature(feat):
                geom = feat.geometry()
                if geom.isMultipart():
                    lm = geom.asMultiPolyline()
                    l = []
                    for ls in lm:
                        p = func(ls, **arguments)
                        l2 = []
                        for n in range(p.n_points):
                            l2.append(QgsPoint(p.x[n], p.y[n]))
                        if len(l2) > 1:
                            l.append(l2)
                    if len(l) > 1:
                        fet.setGeometry(QgsGeometry.fromMultiPolyline(l))
                    elif len(l) == 1: #jesli z obiektu wieloczesciowego zostaje tylko jedna linia (np. przy usuwaniu malych obiektow)
                        fet.setGeometry(QgsGeometry.fromPolyline(l[0]))
                else:
                    ls = geom.asPolyline()
                    p = func(ls, **arguments)
                    l = []
                    for n in range(p.n_points):
                        l.append(QgsPoint(p.x[n], p.y[n]))
                    if len(l) > 1:
                        fet.setGeometry(QgsGeometry.fromPolyline(l))
                    else:
                        continue #jak linia jest pusta to przejdz do nastepnej
                fet.setAttributeMap(feat.attributeMap())
                mProvider.addFeatures([fet])
            mLayer.updateFieldMap()
            mLayer.updateExtents()
            return mLayer

        else: #write shapefile on disk
            writer = QgsVectorFileWriter(oPath, iProvider.encoding(), fields, QGis.WKBLineString, iLayer.srs())
            if writer.hasError() != QgsVectorFileWriter.NoError:
                QMessageBox.critical(None, 'Generalizer', 'Error when creating shapefile: %s' % (writer.hasError()))

            while iProvider.nextFeature(feat):
                geom = feat.geometry()
                if geom.isMultipart():
                    lm = geom.asMultiPolyline()
                    #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(lm) )
                    l = []
                    for ls in lm:
                        p = func(ls, **arguments)
                        l2 = []
                        #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(p.n_points) )
                        for n in range(p.n_points):
                            l2.append(QgsPoint(p.x[n], p.y[n]))
                        if len(l2) > 1:
                            l.append(l2)
                    if len(l) > 1:
                        #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(l) )
                        fet.setGeometry(QgsGeometry.fromMultiPolyline(l))
                else:
                    ls = geom.asPolyline()
                    #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(ls) )
                    p = func(ls, **arguments)
                    l = []
                    for n in range(p.n_points):
                        l.append(QgsPoint(p.x[n], p.y[n]))

                    if len(l) > 1:
                        #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(l) )
                        fet.setGeometry(QgsGeometry.fromPolyline(l))
                fet.setAttributeMap(feat.attributeMap())
                writer.addFeature(fet)

            del writer
            return self.ui.eOutput.text()


    def batchGeneralize(self, layers):
        outNames = []
        for layer in layers:
            vLayer = getMapLayerByName(layer)
            for i in range(self.ui.tblBatchAlg.rowCount()):
                #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(i) )
                alg = self.ui.tblBatchAlg.item(i, 0).text()
                func = self.GetFunction(alg)

                par1 = self.ui.tblBatchAlg.cellWidget(i,1).value()
                if not func in [self.remove, self.douglas_peucker, self.vertex_reduction, self.boyle, self.jenks, self.reumann_witkam]:
                    par2 = self.ui.tblBatchAlg.cellWidget(i,2).value()
                else:
                    par2 = -1
                #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(par2) )

                arguments = self.GetArguments(par1, par2)
                if self.ui.cbOutDir.isChecked() and i == self.ui.tblBatchAlg.rowCount()-1:
                    #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(i) )
                    path = self.ui.eDir.text()
                    if path.contains("\\"):
                        out_name = path + '\\' + layer + '_new.shp'
                    else:
                        out_name = path + '/' + layer + '_new.shp'
                    outNames.append(out_name)
                    vLayer = self.doGeneralize(layer, vLayer, out_name, func, arguments)
                else:
                    vLayer = self.doGeneralize(layer, vLayer, 'memory', func, arguments)

            if not self.ui.cbOutDir.isChecked():
                QgsMapLayerRegistry.instance().addMapLayer(vLayer)

        if self.ui.cbOutDir.isChecked():
            self.LoadLayers(outNames)



    def generalize(self):
        if self.ui.cbBatch.isChecked():
            if self.ui.cbOutDir.isChecked():
                if self.ui.eDir.text() == '':
                    QMessageBox.critical(None, 'Generalizer', 'Enter output directory!')
                    return


            layers = [self.ui.lstLayers.item(i).text() for i in range(self.ui.lstLayers.count()) if self.ui.lstLayers.item(i).checkState() ]
            self.batchGeneralize(layers)
            #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(layers) )
        else:
            if self.ui.cbInput.currentText() == '':
                QMessageBox.critical(None, 'Generalizer', 'No line layers!')
                return

            arguments = self.GetArguments()
            #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(arguments) )
            if arguments == None:
                return

            func = self.GetFunction(self.ui.cbAlgorithm.currentText())
            if self.ui.cbOutFile.isChecked():
                if self.ui.eOutput.text() == '':
                    QMessageBox.critical(None, 'Generalizer', 'Enter output file name!')
                    return
                filePath = self.doGeneralize(self.ui.cbInput.currentText(), getMapLayerByName(self.ui.cbInput.currentText()), self.ui.eOutput.text(), func, arguments)
                self.LoadLayers([filePath])
            else:
                mLayer = self.doGeneralize(self.ui.cbInput.currentText(), getMapLayerByName(self.ui.cbInput.currentText()), 'memory', func, arguments)
                QgsMapLayerRegistry.instance().addMapLayer(mLayer)

        #self.close()
        #refresh layer list
        self.layerList = getLayersNames()
        self.ui.cbInput.clear()
        self.ui.lstLayers.clear()
        self.ui.cbInput.addItems(self.layerList)
        self.ui.lstLayers.addItems(self.layerList)
        [self.ui.lstLayers.item(i).setCheckState(Qt.Unchecked) for i in range(self.ui.lstLayers.count()) ]

    def remove(self, l, **kwargs):
        #Remove Small Objects
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
        #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str( p.x ) )

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
        #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(p.n_points) )
        n = smooth.chaiken(p, kwargs['chaiken_level'], kwargs['chaiken_weight'])

        return p

    def vertex_reduction(self,l,  **kwargs):
        #Vertex Reduction
        #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(l) )
        p = points.Vect_new_line_struct(l)
        n = simplify.vertex_reduction(p, kwargs['reduction_thresh'])

        return p

    def douglas_peucker(self,l,  **kwargs):
        #Douglas-peucker Algorithm
        tmp = simplify.douglas_peucker(l, kwargs['dp_thresh'])
        p = points.Vect_new_line_struct(tmp)

        return p

    def lang(self,l,  **kwargs):
        #Vertex Reduction
        p = points.Vect_new_line_struct(l)
        n = simplify.lang(p, kwargs['lang_thresh'], kwargs['lang_LA'])

        return p

    def hermite(self,l,  **kwargs):
        #Vertex Reduction
        p = points.Vect_new_line_struct(l)
        n = smooth.hermite(p, kwargs['hermite_thresh'], kwargs['hermite_tightness'])

        return p

    def jenks(self,l,  **kwargs):
        #Jenk's Algorithm
        #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str(kwargs['jenks_angle']) )
        p = points.Vect_new_line_struct(l)
        n = simplify.jenks(p, kwargs['jenks_thresh'], kwargs['jenks_angle'])

        return p

    def snakes(self,l,  **kwargs):
        #Snakes
        p = points.Vect_new_line_struct(l)
        n = smooth.snakes(p, kwargs['snakes_alpha'], kwargs['snakes_beta'])

        return p

    def reumann_witkam(self,l,  **kwargs):
        #Snakes
        p = points.Vect_new_line_struct(l)
        n = simplify.reumann_witkam(p, kwargs['rw_thresh'])

        return p


def getLayersNames():
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    layerlist = []
    for name, layer in layermap.iteritems():
        if layer.type() == QgsMapLayer.VectorLayer:
            if layer.geometryType() == QGis.Line:
                layerlist.append( unicode( layer.name() ) )

    return layerlist

def getMapLayerByName(myName):
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layermap.iteritems():
        if layer.name() == myName:
            if layer.isValid():
                return layer
            else:
                return None