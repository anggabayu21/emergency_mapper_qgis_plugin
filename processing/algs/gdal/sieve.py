# -*- coding: utf-8 -*-

"""
***************************************************************************
    sieve.py
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

from qgis.PyQt.QtGui import QIcon

from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm

from processing.core.parameters import ParameterRaster
from processing.core.parameters import ParameterSelection
from processing.core.parameters import ParameterNumber
from processing.core.outputs import OutputRaster

from processing.tools.system import isWindows

from processing.algs.gdal.GdalUtils import GdalUtils

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class sieve(GdalAlgorithm):

    INPUT = 'INPUT'
    THRESHOLD = 'THRESHOLD'
    CONNECTIONS = 'CONNECTIONS'
    OUTPUT = 'OUTPUT'

    PIXEL_CONNECTIONS = ['4', '8']

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'gdaltools', 'sieve.png'))

    def defineCharacteristics(self):
        self.name, self.i18n_name = self.trAlgorithm('Sieve')
        self.group, self.i18n_group = self.trAlgorithm('[GDAL] Analysis')
        self.addParameter(ParameterRaster(self.INPUT, self.tr('Input layer'), False))
        self.addParameter(ParameterNumber(self.THRESHOLD,
                                          self.tr('Threshold'), 0, 9999, 2))
        self.addParameter(ParameterSelection(self.CONNECTIONS,
                                             self.tr('Pixel connection'), self.PIXEL_CONNECTIONS, 0))

        self.addOutput(OutputRaster(self.OUTPUT, self.tr('Sieved')))

    def getConsoleCommands(self):
        output = self.getOutputValue(self.OUTPUT)

        arguments = []
        arguments.append('-st')
        arguments.append(unicode(self.getParameterValue(self.THRESHOLD)))

        arguments.append('-' +
                         self.PIXEL_CONNECTIONS[self.getParameterValue(
                                                self.CONNECTIONS)])

        arguments.append('-of')
        arguments.append(GdalUtils.getFormatShortNameFromFilename(output))

        arguments.append(self.getParameterValue(self.INPUT))
        arguments.append(output)

        commands = []
        if isWindows():
            commands = ['cmd.exe', '/C ', 'gdal_sieve.bat',
                        GdalUtils.escapeAndJoin(arguments)]
        else:
            commands = ['gdal_sieve.py', GdalUtils.escapeAndJoin(arguments)]

        return commands