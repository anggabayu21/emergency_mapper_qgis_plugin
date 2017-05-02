# coding=utf-8
"""Test class for select_parameter_widget."""


import unittest

from PyQt4.QtGui import QApplication

from select_parameter import SelectParameter


from qt_widgets.select_parameter_widget import SelectParameterWidget


class TestSelectParameterWidget(unittest.TestCase):
    """Test for SelectParameterWidget"""
    application = QApplication([])

    def test_init(self):
        select_parameter = SelectParameter()
        select_parameter.name = 'Select Affected Field'
        select_parameter.is_required = True
        select_parameter.help_text = 'Column used for affected field'
        select_parameter.description = (
            'Column used for affected field in the vector')
        select_parameter.element_type = str
        select_parameter.options_list = [
            'FLOODPRONE', 'affected', 'floodprone', 'yes/no',
            '\xddounicode test']
        select_parameter.value = 'affected'

        widget = SelectParameterWidget(select_parameter)

        expected_value = select_parameter.value
        real_value = widget.get_parameter().value
        self.assertEqual(expected_value, real_value)

        widget.input.setCurrentIndex(0)
        real_value = widget.get_parameter().value
        self.assertEqual(real_value, select_parameter.options_list[0])

    def test_set_choice(self):
        """Test for set_choice method."""
        select_parameter = SelectParameter()
        select_parameter.name = 'Select Affected Field'
        select_parameter.is_required = True
        select_parameter.help_text = 'Column used for affected field'
        select_parameter.description = (
            'Column used for affected field in the vector')
        select_parameter.element_type = str
        select_parameter.options_list = [
            'FLOODPRONE', 'affected', 'floodprone', 'yes/no',
            '\xddounicode test']
        select_parameter.value = 'affected'

        widget = SelectParameterWidget(select_parameter)

        widget.set_choice('floodprone')
        real_value = widget.get_parameter().value
        self.assertEqual('floodprone', real_value)
