# -*- coding: utf-8 -*-

"""
***************************************************************************
    Centroids.py
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

# This will get replaced with a git SHA1 when you do a git archive323

__revision__ = '93c55caa41f16a598bbdb1893892cbb342e150cf'

import os

from qgis.PyQt.QtGui import QIcon

from qgis.core import QGis, QgsGeometry, QgsFeature

from inasafe_extras.processing.core.GeoAlgorithm import GeoAlgorithm
from inasafe_extras.processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from inasafe_extras.processing.core.parameters import ParameterVector
from inasafe_extras.processing.core.outputs import OutputVector
from inasafe_extras.processing.tools import dataobjects, vector

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class Centroids(GeoAlgorithm):

    INPUT_LAYER = 'INPUT_LAYER'
    OUTPUT_LAYER = 'OUTPUT_LAYER'

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'ftools', 'centroids.png'))

    def defineCharacteristics(self):
        self.name, self.i18n_name = self.trAlgorithm('Polygon centroids')
        self.group, self.i18n_group = self.trAlgorithm('Vector geometry tools')

        self.addParameter(ParameterVector(self.INPUT_LAYER,
                                          self.tr('Input layer'), [ParameterVector.VECTOR_TYPE_POLYGON]))

        self.addOutput(OutputVector(self.OUTPUT_LAYER, self.tr('Centroids')))

    def processAlgorithm(self, progress):
        layer = dataobjects.getObjectFromUri(
            self.getParameterValue(self.INPUT_LAYER))

        writer = self.getOutputFromName(
            self.OUTPUT_LAYER).getVectorWriter(
                layer.fields(),
                QGis.WKBPoint,
                layer.crs())

        outFeat = QgsFeature()

        features = vector.features(layer)
        total = 100.0 / len(features)
        for current, feat in enumerate(features):
            inGeom = feat.geometry()
            attrs = feat.attributes()

            if not inGeom:
                outGeom = QgsGeometry(None)
            else:
                outGeom = QgsGeometry(inGeom.centroid())
                if not outGeom:
                    raise GeoAlgorithmExecutionException(
                        self.tr('Error calculating centroid'))

            outFeat.setGeometry(outGeom)
            outFeat.setAttributes(attrs)
            writer.addFeature(outFeat)
            progress.setPercentage(int(current * total))

        del writer
