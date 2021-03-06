# -*- coding: utf-8 -*-

"""
***************************************************************************
    ContextAction.py
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


from qgis.PyQt.QtCore import QCoreApplication


class ContextAction:

    def setData(self, itemData, toolbox):
        self.itemData = itemData
        self.toolbox = toolbox

    def tr(self, string, context=''):
        if context == '':
            context = 'ContextAction'
        return QCoreApplication.translate(context, string)
