# -*- coding: utf-8 -*-

"""
***************************************************************************
    BarPlot.py
    ---------------------
    Date                 : January 2013
    Copyright            : (C) 2013 by Victor Olaya
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
__date__ = 'January 2013'
__copyright__ = '(C) 2013, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '93c55caa41f16a598bbdb1893892cbb342e150cf'

import matplotlib.pyplot as plt
import matplotlib.pylab as lab
from matplotlib.pyplot import figure
import numpy as np

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterTable
from processing.core.parameters import ParameterTableField
from processing.core.outputs import OutputHTML
from processing.tools import vector
from processing.tools import dataobjects


class PolarPlot(GeoAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    NAME_FIELD = 'NAME_FIELD'
    VALUE_FIELD = 'VALUE_FIELD'

    def defineCharacteristics(self):
        self.name, self.i18n_name = self.trAlgorithm('Polar plot')
        self.group, self.i18n_group = self.trAlgorithm('Graphics')

        self.addParameter(ParameterTable(self.INPUT,
                                         self.tr('Input table')))
        self.addParameter(ParameterTableField(self.NAME_FIELD,
                                              self.tr('Category name field'), self.INPUT))
        self.addParameter(ParameterTableField(self.VALUE_FIELD,
                                              self.tr('Value field'), self.INPUT))

        self.addOutput(OutputHTML(self.OUTPUT, self.tr('Polar plot')))

    def processAlgorithm(self, progress):
        layer = dataobjects.getObjectFromUri(
            self.getParameterValue(self.INPUT))
        namefieldname = self.getParameterValue(self.NAME_FIELD)
        valuefieldname = self.getParameterValue(self.VALUE_FIELD)

        output = self.getOutputValue(self.OUTPUT)

        values = vector.values(layer, namefieldname, valuefieldname)
        plt.close()
        fig = figure(figsize=(8, 8))
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
        N = len(values[valuefieldname])
        theta = np.arange(0.0, 2 * np.pi, 2 * np.pi / N)
        radii = values[valuefieldname]
        width = 2 * np.pi / N
        ax.bar(theta, radii, width=width, bottom=0.0)
        plotFilename = output + '.png'
        lab.savefig(plotFilename)
        f = open(output, 'w')
        f.write('<html><img src="' + plotFilename + '"/></html>')
        f.close()
