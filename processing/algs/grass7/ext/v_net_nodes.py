# -*- coding: utf-8 -*-

"""
***************************************************************************
    v_net_nodes.py
    ---------------------
    Date                 : December 2015
    Copyright            : (C) 2015 by Médéric Ribreux
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
__date__ = 'December 2015'
__copyright__ = '(C) 2015, Médéric Ribreux'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '93c55caa41f16a598bbdb1893892cbb342e150cf'

from .v_net import variableOutput


def processOutputs(alg):
    outputParameter = {u"output": [u"point", 2]}
    variableOutput(alg, outputParameter)
