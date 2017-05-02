# -*- coding: utf-8 -*-

"""
***************************************************************************
    r_li_edgedensity_ascii.py
    -------------------------
    Date                 : February 2016
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
__date__ = 'February 2016'
__copyright__ = '(C) 2016, Médéric Ribreux'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '93c55caa41f16a598bbdb1893892cbb342e150cf'

from r_li import checkMovingWindow, configFile, moveOutputTxtFile


def checkParameterValuesBeforeExecuting(alg):
    return checkMovingWindow(alg, True)


def processCommand(alg):
    configFile(alg, True)


def processOutputs(alg):
    moveOutputTxtFile(alg)
