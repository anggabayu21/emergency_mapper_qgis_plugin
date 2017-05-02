# -*- coding: utf-8 -*-

"""
***************************************************************************
    i_pca.py
    --------
    Date                 : March 2016
    Copyright            : (C) 2016 by Médéric Ribreux
    Email                : medspx at medspx dot fr
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Médéric Ribreux'
__date__ = 'March 2016'
__copyright__ = '(C) 2016, Médéric Ribreux'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '93c55caa41f16a598bbdb1893892cbb342e150cf'

from i import multipleOutputDir, verifyRasterNum
from processing.core.parameters import getParameterFromString


def checkParameterValuesBeforeExecuting(alg):
    return verifyRasterNum(alg, 'input', 2)


def processCommand(alg):
    # Remove output
    output = alg.getOutputFromName('output')
    alg.removeOutputFromName('output')

    # Create output parameter
    param = getParameterFromString("ParameterString|output|output basename|None|False|False")
    param.value = alg.getTempFilename()
    alg.addParameter(param)

    alg.processCommand()
    # re-add output
    alg.addOutput(output)


def processOutputs(alg):
    param = alg.getParameterFromName('output')
    multipleOutputDir(alg, 'output', param.value)

    # Delete output parameter
    alg.parameters.remove(param)
