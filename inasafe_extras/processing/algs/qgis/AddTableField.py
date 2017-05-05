# -*- coding: utf-8 -*-

"""
***************************************************************************
    AddTableField.py
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

from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsField, QgsFeature
from inasafe_extras.processing.core.GeoAlgorithm import GeoAlgorithm
from inasafe_extras.processing.core.parameters import ParameterVector
from inasafe_extras.processing.core.parameters import ParameterString
from inasafe_extras.processing.core.parameters import ParameterNumber
from inasafe_extras.processing.core.parameters import ParameterSelection
from inasafe_extras.processing.core.outputs import OutputVector
from inasafe_extras.processing.tools import dataobjects, vector


class AddTableField(GeoAlgorithm):

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    FIELD_NAME = 'FIELD_NAME'
    FIELD_TYPE = 'FIELD_TYPE'
    FIELD_LENGTH = 'FIELD_LENGTH'
    FIELD_PRECISION = 'FIELD_PRECISION'

    TYPES = [QVariant.Int, QVariant.Double, QVariant.String]

    def defineCharacteristics(self):
        self.name, self.i18n_name = self.trAlgorithm('Add field to attributes table')
        self.group, self.i18n_group = self.trAlgorithm('Vector table tools')

        self.type_names = [self.tr('Integer'),
                           self.tr('Float'),
                           self.tr('String')]

        self.addParameter(ParameterVector(self.INPUT_LAYER,
                                          self.tr('Input layer'), [ParameterVector.VECTOR_TYPE_ANY], False))
        self.addParameter(ParameterString(self.FIELD_NAME,
                                          self.tr('Field name')))
        self.addParameter(ParameterSelection(self.FIELD_TYPE,
                                             self.tr('Field type'), self.type_names))
        self.addParameter(ParameterNumber(self.FIELD_LENGTH,
                                          self.tr('Field length'), 1, 255, 10))
        self.addParameter(ParameterNumber(self.FIELD_PRECISION,
                                          self.tr('Field precision'), 0, 10, 0))
        self.addOutput(OutputVector(
            self.OUTPUT_LAYER, self.tr('Added')))

    def processAlgorithm(self, progress):
        fieldType = self.getParameterValue(self.FIELD_TYPE)
        fieldName = self.getParameterValue(self.FIELD_NAME)
        fieldLength = self.getParameterValue(self.FIELD_LENGTH)
        fieldPrecision = self.getParameterValue(self.FIELD_PRECISION)
        output = self.getOutputFromName(self.OUTPUT_LAYER)

        layer = dataobjects.getObjectFromUri(
            self.getParameterValue(self.INPUT_LAYER))

        fields = layer.fields()
        fields.append(QgsField(fieldName, self.TYPES[fieldType], '',
                               fieldLength, fieldPrecision))
        writer = output.getVectorWriter(fields, layer.wkbType(),
                                        layer.crs())
        outFeat = QgsFeature()
        features = vector.features(layer)
        total = 100.0 / len(features)
        for current, feat in enumerate(features):
            progress.setPercentage(int(current * total))
            geom = feat.geometry()
            outFeat.setGeometry(geom)
            atMap = feat.attributes()
            atMap.append(None)
            outFeat.setAttributes(atMap)
            writer.addFeature(outFeat)
        del writer
