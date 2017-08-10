# -*- coding: utf-8 -*-

"""
***************************************************************************
    rasterize.py
    ---------------------
    Date                 : September 2013
    Copyright            : (C) 2013 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'September 2013'
__copyright__ = '(C) 2013, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '93c55caa41f16a598bbdb1893892cbb342e150cf'

import os

from qgis.PyQt.QtGui import QIcon

from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterExtent
from processing.core.parameters import ParameterTableField
from processing.core.parameters import ParameterSelection
from processing.core.parameters import ParameterNumber
from processing.core.parameters import ParameterBoolean
from processing.core.parameters import ParameterString
from processing.core.outputs import OutputRaster

from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils

from processing.tools.vector import ogrConnectionString, ogrLayerName

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class rasterize(GdalAlgorithm):

    INPUT = 'INPUT'
    FIELD = 'FIELD'
    DIMENSIONS = 'DIMENSIONS'
    WIDTH = 'WIDTH'
    HEIGHT = 'HEIGHT'
    EXTRA = 'EXTRA'
    RTYPE = 'RTYPE'
    OUTPUT = 'OUTPUT'
    TYPE = ['Byte', 'Int16', 'UInt16', 'UInt32', 'Int32', 'Float32', 'Float64']
    NO_DATA = 'NO_DATA'
    TILED = 'TILED'
    COMPRESS = 'COMPRESS'
    JPEGCOMPRESSION = 'JPEGCOMPRESSION'
    PREDICTOR = 'PREDICTOR'
    ZLEVEL = 'ZLEVEL'
    BIGTIFF = 'BIGTIFF'
    BIGTIFFTYPE = ['', 'YES', 'NO', 'IF_NEEDED', 'IF_SAFER']
    COMPRESSTYPE = ['NONE', 'JPEG', 'LZW', 'PACKBITS', 'DEFLATE']
    TFW = 'TFW'
    RAST_EXT = 'RAST_EXT'

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'gdaltools', 'rasterize.png'))

    def commandLineName(self):
        return "gdalogr:rasterize"

    def defineCharacteristics(self):
        self.name, self.i18n_name = self.trAlgorithm('Rasterize (vector to raster)')
        self.group, self.i18n_group = self.trAlgorithm('[GDAL] Conversion')
        self.addParameter(ParameterVector(self.INPUT, self.tr('Input layer')))
        self.addParameter(ParameterTableField(self.FIELD,
                                              self.tr('Attribute field'), self.INPUT))
        self.addParameter(ParameterSelection(self.DIMENSIONS,
                                             self.tr('Set output raster size (ignored if above option is checked)'),
                                             ['Output size in pixels', 'Output resolution in map units per pixel'], 1))
        self.addParameter(ParameterNumber(self.WIDTH,
                                          self.tr('Horizontal'), 0.0, 99999999.999999, 100.0))
        self.addParameter(ParameterNumber(self.HEIGHT,
                                          self.tr('Vertical'), 0.0, 99999999.999999, 100.0))
        self.addParameter(ParameterExtent(self.RAST_EXT, self.tr('Raster extent')))

        params = []
        params.append(ParameterSelection(self.RTYPE, self.tr('Raster type'),
                                         self.TYPE, 5))
        params.append(ParameterString(self.NO_DATA,
                                      self.tr("Nodata value"),
                                      '', optional=True))
        params.append(ParameterSelection(self.COMPRESS,
                                         self.tr('GeoTIFF options. Compression type:'), self.COMPRESSTYPE, 4))
        params.append(ParameterNumber(self.JPEGCOMPRESSION,
                                      self.tr('Set the JPEG compression level'),
                                      1, 100, 75))
        params.append(ParameterNumber(self.ZLEVEL,
                                      self.tr('Set the DEFLATE compression level'),
                                      1, 9, 6))
        params.append(ParameterNumber(self.PREDICTOR,
                                      self.tr('Set the predictor for LZW or DEFLATE compression'),
                                      1, 3, 1))
        params.append(ParameterBoolean(self.TILED,
                                       self.tr('Create tiled output (only used for the GTiff format)'), False))
        params.append(ParameterSelection(self.BIGTIFF,
                                         self.tr('Control whether the created file is a BigTIFF or a classic TIFF'), self.BIGTIFFTYPE, 0))
        self.addParameter(ParameterBoolean(self.TFW,
                                           self.tr('Force the generation of an associated ESRI world file (.tfw)'), False))
        params.append(ParameterString(self.EXTRA,
                                      self.tr('Additional creation parameters'), '', optional=True))

        for param in params:
            param.isAdvanced = True
            self.addParameter(param)

        self.addOutput(OutputRaster(self.OUTPUT,
                                    self.tr('Rasterized')))

    def getConsoleCommands(self):
        inLayer = self.getParameterValue(self.INPUT)
        ogrLayer = ogrConnectionString(inLayer)[1:-1]
        noData = self.getParameterValue(self.NO_DATA)
        if noData is not None:
            noData = unicode(noData)
        jpegcompression = unicode(self.getParameterValue(self.JPEGCOMPRESSION))
        predictor = unicode(self.getParameterValue(self.PREDICTOR))
        zlevel = unicode(self.getParameterValue(self.ZLEVEL))
        tiled = unicode(self.getParameterValue(self.TILED))
        compress = self.COMPRESSTYPE[self.getParameterValue(self.COMPRESS)]
        bigtiff = self.BIGTIFFTYPE[self.getParameterValue(self.BIGTIFF)]
        tfw = unicode(self.getParameterValue(self.TFW))
        out = self.getOutputValue(self.OUTPUT)
        extra = self.getParameterValue(self.EXTRA)
        if extra is not None:
            extra = unicode(extra)
        rastext = unicode(self.getParameterValue(self.RAST_EXT))

        arguments = []
        arguments.append('-a')
        arguments.append(unicode(self.getParameterValue(self.FIELD)))

        arguments.append('-ot')
        arguments.append(self.TYPE[self.getParameterValue(self.RTYPE)])
        dimType = self.getParameterValue(self.DIMENSIONS)
        arguments.append('-of')
        arguments.append(GdalUtils.getFormatShortNameFromFilename(out))

        regionCoords = rastext.split(',')
        try:
            rastext = []
            rastext.append('-te')
            rastext.append(regionCoords[0])
            rastext.append(regionCoords[2])
            rastext.append(regionCoords[1])
            rastext.append(regionCoords[3])
        except IndexError:
            rastext = []
        if rastext:
            arguments.extend(rastext)

        if dimType == 0:
            # size in pixels
            arguments.append('-ts')
            arguments.append(unicode(self.getParameterValue(self.WIDTH)))
            arguments.append(unicode(self.getParameterValue(self.HEIGHT)))
        else:
            # resolution in map units per pixel
            arguments.append('-tr')
            arguments.append(unicode(self.getParameterValue(self.WIDTH)))
            arguments.append(unicode(self.getParameterValue(self.HEIGHT)))

        if noData and len(noData) > 0:
            arguments.append('-a_nodata')
            arguments.append(noData)

        if (GdalUtils.getFormatShortNameFromFilename(out) == "GTiff"):
            arguments.append("-co COMPRESS=" + compress)
            if compress == 'JPEG':
                arguments.append("-co JPEG_QUALITY=" + jpegcompression)
            elif (compress == 'LZW') or (compress == 'DEFLATE'):
                arguments.append("-co PREDICTOR=" + predictor)
            if compress == 'DEFLATE':
                arguments.append("-co ZLEVEL=" + zlevel)
            if tiled == "True":
                arguments.append("-co TILED=YES")
            if tfw == "True":
                arguments.append("-co TFW=YES")
            if len(bigtiff) > 0:
                arguments.append("-co BIGTIFF=" + bigtiff)
        if extra and len(extra) > 0:
            arguments.append(extra)
        arguments.append('-l')

        arguments.append(ogrLayerName(inLayer))
        arguments.append(ogrLayer)

        arguments.append(unicode(self.getOutputValue(self.OUTPUT)))
        return ['gdal_rasterize', GdalUtils.escapeAndJoin(arguments)]