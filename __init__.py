# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaVap
                                 A QGIS plugin
 This plugin is to create a map with Sentinel Asia Value Added Product
                             -------------------
        begin                : 2017-03-22
        copyright            : (C) 2017 by GIC - AIT
        email                : anggabayu@ait.asia
        git sha              : 93c55caa41f16a598bbdb1893892cbb342e150cf
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))


PARAMETER_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'inasafe_extras', 'parameters'))
if PARAMETER_DIR not in sys.path:
    sys.path.append(PARAMETER_DIR)


sys.path.extend([os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir))])


# DO NOT REMOVE THIS
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from PyQt4.QtCore import (
    QLocale,
    QTranslator,
    QCoreApplication,
    QSettings)

# Setup internationalisation for the plugin.
#
# See if QGIS wants to override the system locale
# and then see if we can get a valid translation file
# for whatever locale is effectively being used.

override_flag = QSettings().value(
    'locale/overrideFlag', True, type=bool)

if override_flag:
    locale_name = QSettings().value('locale/userLocale', 'en_US', type=str)
else:
    locale_name = QLocale.system().name()
    # NOTES: we split the locale name because we need the first two
    # character i.e. 'id', 'af, etc
    locale_name = str(locale_name).split('_')[0]

# Also set the system locale to the user overridden local
# so that the inasafe library functions gettext will work
# .. see:: :py:func:`common.utilities`
os.environ['LANG'] = str(locale_name)

root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
translation_path = os.path.join(
    root, 'i18n',
    'inasafe_' + str(locale_name) + '.qm')

if os.path.exists(translation_path):
    translator = QTranslator()
    result = translator.load(translation_path)
    if not result:
        message = 'Failed to load translation for %s' % locale_name
        raise Exception(message)
    # noinspection PyTypeChecker,PyCallByClass
    QCoreApplication.installTranslator(translator)


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SaVap class from file SaVap.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .sa_vap import SaVap
    return SaVap(iface)
