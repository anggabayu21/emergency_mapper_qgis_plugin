# -*- coding: utf-8 -*-

"""
***************************************************************************
    Boundary.py
    --------------
    Date                 : July 2016
    Copyright            : (C) 2016 by Nyall Dawson
    Email                : nyall dot dawson at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Nyall Dawson'
__date__ = 'July 2016'
__copyright__ = '(C) 2016, Nyall Dawson'

# This will get replaced with a git SHA1 when you do a git archive323

__revision__ = '93c55caa41f16a598bbdb1893892cbb342e150cf'

import os

from qgis.core import QgsGeometry, QGis

from qgis.PyQt.QtGui import QIcon

from inasafe_extras.processing.core.GeoAlgorithm import GeoAlgorithm
from inasafe_extras.processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from inasafe_extras.processing.core.parameters import ParameterVector
from inasafe_extras.processing.core.outputs import OutputVector
from inasafe_extras.processing.tools import dataobjects, vector

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class Boundary(GeoAlgorithm):

    INPUT_LAYER = 'INPUT_LAYER'
    OUTPUT_LAYER = 'OUTPUT_LAYER'

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'ftools', 'convex_hull.png'))

    def defineCharacteristics(self):
        self.name, self.i18n_name = self.trAlgorithm('Boundary')
        self.group, self.i18n_group = self.trAlgorithm('Vector geometry tools')

        self.addParameter(ParameterVector(self.INPUT_LAYER,
                                          self.tr('Input layer'), [ParameterVector.VECTOR_TYPE_LINE,
                                                                   ParameterVector.VECTOR_TYPE_POLYGON]))
        self.addOutput(OutputVector(self.OUTPUT_LAYER, self.tr('Boundary')))

    def processAlgorithm(self, progress):
        layer = dataobjects.getObjectFromUri(
            self.getParameterValue(self.INPUT_LAYER))

        if layer.geometryType() == QGis.Line:
            output_wkb = QGis.WKBMultiPoint
        elif layer.geometryType() == QGis.Polygon:
            output_wkb = QGis.WKBLineString

        writer = self.getOutputFromName(
            self.OUTPUT_LAYER).getVectorWriter(
                layer.fields(),
                output_wkb,
                layer.crs())

        features = vector.features(layer)
        total = 100.0 / len(features)

        for current, input_feature in enumerate(features):
            output_feature = input_feature
            if input_feature.constGeometry():
                input_geometry = QgsGeometry(input_feature.geometry())
                output_geometry = QgsGeometry(input_geometry.geometry().boundary())
                if not output_geometry:
                    raise GeoAlgorithmExecutionException(
                        self.tr('Error calculating boundary'))

                output_feature.setGeometry(output_geometry)

            writer.addFeature(output_feature)
            progress.setPercentage(int(current * total))

        del writer
