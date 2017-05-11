# coding=utf-8
"""Tests for select parameter."""

from unittest import TestCase

from select_parameter import SelectParameter
from parameter_exceptions import ValueNotAllowedException

__author__ = 'ismailsunni'
__project_name__ = 'parameters'
__filename__ = 'test_select_parameter'
__date__ = '05/10/2016'
__copyright__ = 'imajimatika@gmail.com'

selected = 'one'

options = ['one', 'two', 'three', 'four', 'five']


class TestSelectParameter(TestCase):
    """Test For Select Parameter."""

    def setUp(self):
        self.parameter = SelectParameter()
        self.parameter.is_required = True
        self.parameter.element_type = str

        self.parameter.options_list = options
        self.parameter.value = selected

    def test_set_value(self):
        self.parameter.value = selected
        self.assertEqual(selected, self.parameter.value)

    def test_not_allowed_value(self):
        with self.assertRaises(ValueNotAllowedException):
            self.parameter.value = 1
