# coding=utf-8
"""Docstring for this file."""
__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'float_parameter_widget'
__date__ = '8/19/14'
__copyright__ = 'ismail@kartoza.com'

from PyQt4.QtGui import QSpinBox

from qt_widgets.numeric_parameter_widget import NumericParameterWidget


class IntegerParameterWidget(NumericParameterWidget):
    """Widget class for Integer parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameter: A IntegerParameter object.
        :type parameter: IntegerParameter

        """
        super(IntegerParameterWidget, self).__init__(parameter, parent)

        self._input = QSpinBox()
        self._input.setValue(self._parameter.value)
        self._input.setMinimum(self._parameter.minimum_allowed_value)
        self._input.setMaximum(self._parameter.maximum_allowed_value)
        tool_tip = 'Choose a number between %d and %d' % (
            self._parameter.minimum_allowed_value,
            self._parameter.maximum_allowed_value)
        self._input.setToolTip(tool_tip)

        self._input.setSizePolicy(self._spin_box_size_policy)

        self.inner_input_layout.addWidget(self._input)
        self.inner_input_layout.addWidget(self._unit_widget)
