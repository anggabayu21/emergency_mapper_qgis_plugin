# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SelectExposureDataBase
                                 A QGIS plugin
 SA VAP links points to photos
                             -------------------
        begin                : 2017-03-16
        git sha              : 93c55caa41f16a598bbdb1893892cbb342e150cf
        copyright            : (C) 2017 by Bayu
        email                : anggabayu@ait.asia
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'wizard_quickmap_1_base.ui'))


class WizardQuickmap1(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(WizardQuickmap1, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.open_bool = False

    def closeEvent(self, evnt):
        #evnt.ignore()
        self.open_bool = False

    def showEvent(self, evnt):
        self.open_bool = True

    def getOpenBool(self):
        return self.open_bool  
    

        
