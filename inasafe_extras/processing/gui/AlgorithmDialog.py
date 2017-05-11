# -*- coding: utf-8 -*-

"""
***************************************************************************
    AlgorithmDialog.py
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

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox, QApplication, QPushButton, QWidget, QVBoxLayout
from qgis.PyQt.QtGui import QCursor, QColor, QPalette

from qgis.core import QgsMapLayerRegistry, QgsExpressionContext, QgsExpressionContextUtils, QgsExpression

from inasafe_extras.processing.core.ProcessingLog import ProcessingLog
from inasafe_extras.processing.core.ProcessingConfig import ProcessingConfig

from inasafe_extras.processing.gui.BatchAlgorithmDialog import BatchAlgorithmDialog
from inasafe_extras.processing.gui.ParametersPanel import ParametersPanel
from inasafe_extras.processing.gui.AlgorithmDialogBase import AlgorithmDialogBase
from inasafe_extras.processing.gui.AlgorithmExecutor import runalg, runalgIterating
from inasafe_extras.processing.gui.Postprocessing import handleAlgorithmResults

from inasafe_extras.processing.core.parameters import ParameterExtent
from inasafe_extras.processing.core.parameters import ParameterRaster
from inasafe_extras.processing.core.parameters import ParameterVector
from inasafe_extras.processing.core.parameters import ParameterTable
from inasafe_extras.processing.core.parameters import ParameterBoolean
from inasafe_extras.processing.core.parameters import ParameterSelection
from inasafe_extras.processing.core.parameters import ParameterFixedTable
from inasafe_extras.processing.core.parameters import ParameterRange
from inasafe_extras.processing.core.parameters import ParameterTableField
from inasafe_extras.processing.core.parameters import ParameterTableMultipleField
from inasafe_extras.processing.core.parameters import ParameterMultipleInput
from inasafe_extras.processing.core.parameters import ParameterString
from inasafe_extras.processing.core.parameters import ParameterNumber
from inasafe_extras.processing.core.parameters import ParameterFile
from inasafe_extras.processing.core.parameters import ParameterCrs
from inasafe_extras.processing.core.parameters import ParameterPoint
from inasafe_extras.processing.core.parameters import ParameterGeometryPredicate

from inasafe_extras.processing.core.outputs import OutputRaster
from inasafe_extras.processing.core.outputs import OutputVector
from inasafe_extras.processing.core.outputs import OutputTable

from inasafe_extras.processing.tools import dataobjects

from qgis.utils import iface


class AlgorithmDialog(AlgorithmDialogBase):

    def __init__(self, alg):
        AlgorithmDialogBase.__init__(self, alg)

        self.alg = alg

        self.mainWidget = ParametersPanel(self, alg)
        self.setMainWidget()

        self.cornerWidget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 5)
        self.tabWidget.setStyleSheet("QTabBar::tab { height: 30px; }")
        self.runAsBatchButton = QPushButton(self.tr("Run as batch process..."))
        self.runAsBatchButton.clicked.connect(self.runAsBatch)
        layout.addWidget(self.runAsBatchButton)
        self.cornerWidget.setLayout(layout)
        self.tabWidget.setCornerWidget(self.cornerWidget)

        QgsMapLayerRegistry.instance().layerWasAdded.connect(self.mainWidget.layerAdded)
        QgsMapLayerRegistry.instance().layersWillBeRemoved.connect(self.mainWidget.layersWillBeRemoved)

    def runAsBatch(self):
        dlg = BatchAlgorithmDialog(self.alg)
        dlg.exec_()

    def setParamValues(self):
        params = self.alg.parameters
        outputs = self.alg.outputs

        for param in params:
            if param.hidden:
                continue
            if isinstance(param, ParameterExtent):
                continue
            if not self.setParamValue(
                    param, self.mainWidget.valueItems[param.name]):
                raise AlgorithmDialogBase.InvalidParameterValue(
                    param, self.mainWidget.valueItems[param.name])

        for param in params:
            if isinstance(param, ParameterExtent):
                if not self.setParamValue(
                        param, self.mainWidget.valueItems[param.name]):
                    raise AlgorithmDialogBase.InvalidParameterValue(
                        param, self.mainWidget.valueItems[param.name])

        for output in outputs:
            if output.hidden:
                continue
            output.value = self.mainWidget.valueItems[output.name].getValue()
            if isinstance(output, (OutputRaster, OutputVector, OutputTable)):
                output.open = self.mainWidget.checkBoxes[output.name].isChecked()

        return True

    def evaluateExpression(self, text):
        context = QgsExpressionContext()
        context.appendScope(QgsExpressionContextUtils.globalScope())
        context.appendScope(QgsExpressionContextUtils.projectScope())
        exp = QgsExpression(text)
        if exp.hasParserError():
            raise Exception(exp.parserErrorString())
        result = exp.evaluate(context)
        if exp.hasEvalError():
            raise ValueError(exp.evalErrorString())
        return result

    def setParamValue(self, param, widget, alg=None):
        if isinstance(param, ParameterRaster):
            return param.setValue(widget.getValue())
        elif isinstance(param, (ParameterVector, ParameterTable)):
            try:
                return param.setValue(widget.itemData(widget.currentIndex()))
            except:
                return param.setValue(widget.getValue())
        elif isinstance(param, ParameterBoolean):
            return param.setValue(widget.isChecked())
        elif isinstance(param, ParameterSelection):
            return param.setValue(widget.currentIndex())
        elif isinstance(param, ParameterFixedTable):
            return param.setValue(widget.table)
        elif isinstance(param, ParameterRange):
            return param.setValue(widget.getValue())
        elif isinstance(param, ParameterTableField):
            if param.optional and widget.currentIndex() == 0:
                return param.setValue(None)
            return param.setValue(widget.currentText())
        elif isinstance(param, ParameterTableMultipleField):
            if param.optional and len(list(widget.get_selected_items())) == 0:
                return param.setValue(None)
            return param.setValue(list(widget.get_selected_items()))
        elif isinstance(param, ParameterMultipleInput):
            if param.datatype == ParameterMultipleInput.TYPE_FILE:
                return param.setValue(widget.selectedoptions)
            else:
                if param.datatype == ParameterMultipleInput.TYPE_RASTER:
                    options = dataobjects.getRasterLayers(sorting=False)
                elif param.datatype == ParameterMultipleInput.TYPE_VECTOR_ANY:
                    options = dataobjects.getVectorLayers(sorting=False)
                else:
                    options = dataobjects.getVectorLayers([param.datatype], sorting=False)
                return param.setValue([options[i] for i in widget.selectedoptions])
        elif isinstance(param, (ParameterNumber, ParameterFile, ParameterCrs,
                                ParameterExtent, ParameterPoint)):
            return param.setValue(widget.getValue())
        elif isinstance(param, ParameterString):
            if param.multiline:
                text = unicode(widget.toPlainText())
            else:
                text = widget.text()

            if param.evaluateExpressions:
                try:
                    text = self.evaluateExpression(text)
                except:
                    pass
            return param.setValue(text)
        elif isinstance(param, ParameterGeometryPredicate):
            return param.setValue(widget.value())
        else:
            return param.setValue(unicode(widget.text()))

    def checkExtentCRS(self):
        unmatchingCRS = False
        hasExtent = False
        projectCRS = iface.mapCanvas().mapSettings().destinationCrs()
        layers = dataobjects.getAllLayers()
        for param in self.alg.parameters:
            if isinstance(param, (ParameterRaster, ParameterVector, ParameterMultipleInput)):
                if param.value:
                    if isinstance(param, ParameterMultipleInput):
                        inputlayers = param.value.split(';')
                    else:
                        inputlayers = [param.value]
                    for inputlayer in inputlayers:
                        for layer in layers:
                            if layer.source() == inputlayer:
                                if layer.crs() != projectCRS:
                                    unmatchingCRS = True

                        p = dataobjects.getObjectFromUri(inputlayer)
                        if p is not None:
                            if p.crs() != projectCRS:
                                unmatchingCRS = True
            if isinstance(param, ParameterExtent):
                value = self.mainWidget.valueItems[param.name].leText.text().strip()
                if value:
                    hasExtent = True

        return hasExtent and unmatchingCRS

    def accept(self):
        self.settings.setValue("/Processing/dialogBase", self.saveGeometry())

        checkCRS = ProcessingConfig.getSetting(ProcessingConfig.WARN_UNMATCHING_CRS)
        try:
            self.setParamValues()
            if checkCRS and not self.alg.checkInputCRS():
                reply = QMessageBox.question(self, self.tr("Unmatching CRS's"),
                                             self.tr('Layers do not all use the same CRS. This can '
                                                     'cause unexpected results.\nDo you want to '
                                                     'continue?'),
                                             QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            checkExtentCRS = ProcessingConfig.getSetting(ProcessingConfig.WARN_UNMATCHING_EXTENT_CRS)
            if checkExtentCRS and self.checkExtentCRS():
                reply = QMessageBox.question(self, self.tr("Extent CRS"),
                                             self.tr('Extent parameters must use the same CRS as the input layers.\n'
                                                     'Your input layers do not have the same extent as the project, '
                                                     'so the extent might be in a wrong CRS if you have selected it from the canvas.\n'
                                                     'Do you want to continue?'),
                                             QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            msg = self.alg._checkParameterValuesBeforeExecuting()
            if msg:
                QMessageBox.warning(
                    self, self.tr('Unable to execute algorithm'), msg)
                return
            self.btnRun.setEnabled(False)
            self.btnClose.setEnabled(False)
            buttons = self.mainWidget.iterateButtons
            self.iterateParam = None

            for i in range(len(buttons.values())):
                button = buttons.values()[i]
                if button.isChecked():
                    self.iterateParam = buttons.keys()[i]
                    break

            self.progressBar.setMaximum(0)
            self.lblProgress.setText(self.tr('Processing algorithm...'))
            # Make sure the Log tab is visible before executing the algorithm
            try:
                self.tabWidget.setCurrentIndex(1)
                self.repaint()
            except:
                pass

            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

            self.setInfo(
                self.tr('<b>Algorithm %s starting...</b>') % self.alg.name)

            if self.iterateParam:
                if runalgIterating(self.alg, self.iterateParam, self):
                    self.finish()
                else:
                    QApplication.restoreOverrideCursor()
                    self.resetGUI()
            else:
                command = self.alg.getAsCommand()
                if command:
                    ProcessingLog.addToLog(
                        ProcessingLog.LOG_ALGORITHM, command)
                if runalg(self.alg, self):
                    self.finish()
                else:
                    QApplication.restoreOverrideCursor()
                    self.resetGUI()
        except AlgorithmDialogBase.InvalidParameterValue as e:
            try:
                self.buttonBox.accepted.connect(lambda:
                                                e.widget.setPalette(QPalette()))
                palette = e.widget.palette()
                palette.setColor(QPalette.Base, QColor(255, 255, 0))
                e.widget.setPalette(palette)
                self.lblProgress.setText(
                    self.tr('<b>Missing parameter value: %s</b>') % e.parameter.description)
                return
            except:
                QMessageBox.critical(self,
                                     self.tr('Unable to execute algorithm'),
                                     self.tr('Wrong or missing parameter values'))

    def finish(self):
        keepOpen = ProcessingConfig.getSetting(ProcessingConfig.KEEP_DIALOG_OPEN)

        if self.iterateParam is None:
            if not handleAlgorithmResults(self.alg, self, not keepOpen):
                self.resetGUI()
                return

        self.executed = True
        self.setInfo('Algorithm %s finished' % self.alg.name)
        QApplication.restoreOverrideCursor()

        if not keepOpen:
            self.close()
        else:
            self.resetGUI()
            if self.alg.getHTMLOutputsCount() > 0:
                self.setInfo(
                    self.tr('HTML output has been generated by this algorithm.'
                            '\nOpen the results dialog to check it.'))

    def closeEvent(self, evt):
        QgsMapLayerRegistry.instance().layerWasAdded.disconnect(self.mainWidget.layerAdded)
        QgsMapLayerRegistry.instance().layersWillBeRemoved.disconnect(self.mainWidget.layersWillBeRemoved)
        super(AlgorithmDialog, self).closeEvent(evt)
