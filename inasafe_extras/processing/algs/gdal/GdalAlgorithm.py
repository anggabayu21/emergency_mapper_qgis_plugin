# -*- coding: utf-8 -*-

"""
***************************************************************************
    GdalAlgorithm.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '93c55caa41f16a598bbdb1893892cbb342e150cf'

import os
import re

from qgis.PyQt.QtGui import QIcon

from inasafe_extras.processing.core.GeoAlgorithm import GeoAlgorithm
from inasafe_extras.processing.algs.gdal.GdalAlgorithmDialog import GdalAlgorithmDialog
from inasafe_extras.processing.algs.gdal.GdalUtils import GdalUtils
from inasafe_extras.processing.tools import dataobjects

pluginPath = os.path.normpath(os.path.join(
    os.path.split(os.path.dirname(__file__))[0], os.pardir))


class GdalAlgorithm(GeoAlgorithm):

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'gdal.svg'))

    def getCustomParametersDialog(self):
        return GdalAlgorithmDialog(self)

    def processAlgorithm(self, progress):
        commands = self.getConsoleCommands()
        layers = dataobjects.getVectorLayers()
        supported = dataobjects.getSupportedOutputVectorLayerExtensions()
        for i, c in enumerate(commands):
            for layer in layers:
                if layer.source() in c:
                    exported = dataobjects.exportVectorLayer(layer, supported)
                    exportedFileName = os.path.splitext(os.path.split(exported)[1])[0]
                    c = c.replace(layer.source(), exported)
                    if os.path.isfile(layer.source()):
                        fileName = os.path.splitext(os.path.split(layer.source())[1])[0]
                        c = re.sub('[\s]{}[\s]'.format(fileName), ' ' + exportedFileName + ' ', c)
                        c = re.sub('[\s]{}'.format(fileName), ' ' + exportedFileName, c)
                        c = re.sub('["\']{}["\']'.format(fileName), "'" + exportedFileName + "'", c)

            commands[i] = c
        GdalUtils.runGdal(commands, progress)

    def shortHelp(self):
        return self._formatHelp('''This algorithm is based on the GDAL %s module.

                For more info, see the <a href = 'http://www.gdal.org/%s.html'> module help</a>
                ''' % (self.commandName(), self.commandName()))

    def commandName(self):
        alg = self.getCopy()
        for output in alg.outputs:
            output.setValue("dummy")
        for param in alg.parameters:
            param.setValue("1")
        name = alg.getConsoleCommands()[0]
        if name.endswith(".py"):
            name = name[:-3]
        return name