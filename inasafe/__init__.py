# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
 - **Module inasafe.**

This script initializes the plugin, making it known to QGIS.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@kartoza.com'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# DO NOT REMOVE THIS
# Please import module in safe from the safe root, e.g:
# from inasafe.x.y import z
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
import logging

from inasafe.common.custom_logging import setup_logger

setup_logger('SaVap')
