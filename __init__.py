"""
/***************************************************************************
 generalizer
                                 A QGIS plugin
"Lines generalization and smoothing (partially based on v.generalize GRASS module)"
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
 This script initializes the plugin, making it known to QGIS.
"""
from __future__ import absolute_import
def classFactory(iface):
    # load generalizer class from file generalizer
    from .generalizer import generalizer
    return generalizer(iface)
