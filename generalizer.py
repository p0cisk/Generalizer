"""
/***************************************************************************
 generalizer
                                 A QGIS plugin
 Lines generalization (smooth and simplify) based on v.generalize GRASS module
                              -------------------
        begin                : 2011-08-17
        copyright            : (C) 2011 by Piotr Pociask
        email                : ppociask (at) o2 pl
        adapted to QGIS 3    : 2019-11-10 by Sylvain POULAIN
        email				 : sylvain.poulain (at) giscan.com
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
from __future__ import absolute_import
# Import the PyQt and QGIS libraries
from builtins import object
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import QAction


from qgis.core import *
# Initialize Qt resources from file resources.py
from . import resources
# Import the code for the dialog
from .generalizerdialog import generalizerDialog, getLayersNames

class generalizer(object):

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/generalizer/icon.png"), \
            "Generalizer", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect( self.run )

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Generalizer", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&Generalizer",self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        #check if there are loaded line layers
        if len(getLayersNames()) == 0:
            QMessageBox.critical(None, 'Generalizer', 'Load line layer!')
            return

          # create and show the dialog
        dlg = generalizerDialog(self.iface)
        # show the dialog
        dlg.show()
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code
            pass
