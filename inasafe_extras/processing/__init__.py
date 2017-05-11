# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
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

from inasafe_extras.processing.tools.dataobjects import *          # NOQA
from inasafe_extras.processing.tools.general import *              # NOQA
from inasafe_extras.processing.tools.vector import *               # NOQA
from inasafe_extras.processing.tools.raster import *               # NOQA
from inasafe_extras.processing.tools.system import *               # NOQA
#from inasafe_extras.processing.tests.TestData import loadTestData  # NOQA


#def classFactory(iface):
#    from inasafe_extras.processing.ProcessingPlugin import ProcessingPlugin
#    return ProcessingPlugin(iface)
