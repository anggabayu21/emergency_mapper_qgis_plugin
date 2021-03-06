# coding=utf-8
"""Tests for default value parameter."""

from unittest import TestCase

from inasafe.common.parameters.default_value_parameter import (
    DefaultValueParameter)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '4c85bcb847131a3d634744b9ea01083b158493bf'

labels = ['Setting', 'Do not use', 'Custom']
options = [0.1, None]


class TestDefaultValueParameter(TestCase):

    """Test For Default Value Parameter."""

    def setUp(self):
        """Set up common object for testing."""
        self.parameter = DefaultValueParameter()

        self.parameter.labels = labels
        self.parameter.options = options

    def test_default_value(self):
        """Test default value."""
        self.assertEqual(self.parameter.labels, labels)
        self.parameter.value = 0.2
        self.assertEqual(
            self.parameter.options[-1], self.parameter.value)
