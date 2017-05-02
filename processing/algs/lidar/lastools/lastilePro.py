# -*- coding: utf-8 -*-

"""
***************************************************************************
    lastilePro.py
    ---------------------
    Date                 : April 2014 and May 2016
    Copyright            : (C) 2014 by Martin Isenburg
    Email                : martin near rapidlasso point com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Martin Isenburg'
__date__ = 'April 2014'
__copyright__ = '(C) 2014, Martin Isenburg'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '93c55caa41f16a598bbdb1893892cbb342e150cf'

import os
from .LAStoolsUtils import LAStoolsUtils
from .LAStoolsAlgorithm import LAStoolsAlgorithm

from processing.core.parameters import ParameterBoolean
from processing.core.parameters import ParameterNumber
from processing.core.parameters import ParameterString


class lastilePro(LAStoolsAlgorithm):

    TILE_SIZE = "TILE_SIZE"
    BUFFER = "BUFFER"
    FLAG_AS_WITHHELD = "FLAG_AS_WITHHELD"
    EXTRA_PASS = "EXTRA_PASS"
    BASE_NAME = "BASE_NAME"

    def defineCharacteristics(self):
        self.name, self.i18n_name = self.trAlgorithm('lastilePro')
        self.group, self.i18n_group = self.trAlgorithm('LAStools Production')
        self.addParametersPointInputFolderGUI()
        self.addParametersFilesAreFlightlinesGUI()
        self.addParametersApplyFileSourceIdGUI()
        self.addParameter(ParameterNumber(lastilePro.TILE_SIZE,
                                          self.tr("tile size (side length of square tile)"),
                                          0.0, None, 1000.0))
        self.addParameter(ParameterNumber(lastilePro.BUFFER,
                                          self.tr("buffer around each tile (avoids edge artifacts)"),
                                          0.0, None, 25.0))
        self.addParameter(ParameterBoolean(lastilePro.FLAG_AS_WITHHELD,
                                           self.tr("flag buffer points as 'withheld' for easier removal later"), True))
        self.addParameter(ParameterBoolean(lastilePro.EXTRA_PASS,
                                           self.tr("more than 2000 tiles"), False))
        self.addParametersOutputDirectoryGUI()
        self.addParameter(ParameterString(lastilePro.BASE_NAME,
                                          self.tr("tile base name (using sydney.laz creates sydney_274000_4714000.laz)")))
        self.addParametersPointOutputFormatGUI()
        self.addParametersAdditionalGUI()
        self.addParametersVerboseGUI()

    def processAlgorithm(self, progress):
        commands = [os.path.join(LAStoolsUtils.LAStoolsPath(), "bin", "lastile")]
        self.addParametersVerboseCommands(commands)
        self.addParametersPointInputFolderCommands(commands)
        self.addParametersFilesAreFlightlinesCommands(commands)
        self.addParametersApplyFileSourceIdCommands(commands)
        tile_size = self.getParameterValue(lastilePro.TILE_SIZE)
        commands.append("-tile_size")
        commands.append(unicode(tile_size))
        buffer = self.getParameterValue(lastilePro.BUFFER)
        if buffer != 0.0:
            commands.append("-buffer")
            commands.append(unicode(buffer))
        if self.getParameterValue(lastilePro.FLAG_AS_WITHHELD):
            commands.append("-flag_as_withheld")
        if self.getParameterValue(lastilePro.EXTRA_PASS):
            commands.append("-extra_pass")
        self.addParametersOutputDirectoryCommands(commands)
        base_name = self.getParameterValue(lastilePro.BASE_NAME)
        if base_name is not None:
            commands.append("-o")
            commands.append('"' + base_name + '"')
        self.addParametersPointOutputFormatCommands(commands)
        self.addParametersAdditionalCommands(commands)

        LAStoolsUtils.runLAStools(commands, progress)
