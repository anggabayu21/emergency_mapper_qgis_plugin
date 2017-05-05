# -*- coding: utf-8 -*-

"""
***************************************************************************
    ScriptAlgorithmProvider.py
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

import os

from qgis.PyQt.QtGui import QIcon

from inasafe_extras.processing.core.ProcessingConfig import ProcessingConfig, Setting
from inasafe_extras.processing.core.AlgorithmProvider import AlgorithmProvider
from inasafe_extras.processing.gui.EditScriptAction import EditScriptAction
from inasafe_extras.processing.gui.DeleteScriptAction import DeleteScriptAction
from inasafe_extras.processing.gui.CreateNewScriptAction import CreateNewScriptAction
from inasafe_extras.processing.script.ScriptUtils import ScriptUtils
from inasafe_extras.processing.script.AddScriptFromFileAction import AddScriptFromFileAction
from inasafe_extras.processing.gui.GetScriptsAndModels import GetScriptsAction
from inasafe_extras.processing.script.CreateScriptCollectionPluginAction import CreateScriptCollectionPluginAction

pluginPath = os.path.split(os.path.dirname(__file__))[0]


class ScriptAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.actions.extend([CreateNewScriptAction('Create new script',
                                                   CreateNewScriptAction.SCRIPT_PYTHON),
                             AddScriptFromFileAction(),
                             GetScriptsAction(),
                             CreateScriptCollectionPluginAction(), ])
        self.contextMenuActions = \
            [EditScriptAction(EditScriptAction.SCRIPT_PYTHON),
             DeleteScriptAction(DeleteScriptAction.SCRIPT_PYTHON)]

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)
        ProcessingConfig.addSetting(Setting(self.getDescription(),
                                            ScriptUtils.SCRIPTS_FOLDER,
                                            self.tr('Scripts folder', 'ScriptAlgorithmProvider'),
                                            ScriptUtils.defaultScriptsFolder(), valuetype=Setting.MULTIPLE_FOLDERS))

    def unload(self):
        AlgorithmProvider.unload(self)
        ProcessingConfig.addSetting(ScriptUtils.SCRIPTS_FOLDER)

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'script.png'))

    def getName(self):
        return 'script'

    def getDescription(self):
        return self.tr('Scripts', 'ScriptAlgorithmProvider')

    def _loadAlgorithms(self):
        folders = ScriptUtils.scriptsFolders()
        self.algs = []
        for f in folders:
            self.algs.extend(ScriptUtils.loadFromFolder(f))

    def addAlgorithmsFromFolder(self, folder):
        self.algs.extend(ScriptUtils.loadFromFolder(folder))
