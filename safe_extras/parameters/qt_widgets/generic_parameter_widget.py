# coding=utf-8
"""Generic Parameter Widget for this file."""

from PyQt4.QtGui import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QToolButton,
    QGridLayout,
    QSizePolicy)

__author__ = 'ismailsunni'
__project_name = 'parameters'
__filename = 'generic_parameter_widget'
__date__ = '8/21/14'
__copyright__ = 'ismail@kartoza.com'


class GenericParameterWidget(QWidget, object):
    """Widget class for generic parameter."""
    def __init__(self, parameter, parent=None):
        """Constructor

        .. versionadded:: 2.2

        :param parameter: A Generic object.
        :type parameter: GenericParameter

        """
        QWidget.__init__(self, parent)
        self._parameter = parameter

        # Create elements
        # Label (name)
        self.label = QLabel(self._parameter.name)

        # Label (description text)
        # Hacky fix for #1830 - checking the base type
        if isinstance(self._parameter.description, basestring):
            self.description_text_label = QLabel(self._parameter.description)
        else:
            self.description_text_label = QLabel()

        self.description_text_label.setWordWrap(True)

        # Label (help)
        self.help_label = QLabel(self._parameter.help_text)
        self.help_label.setWordWrap(True)
        self.help_label.hide()

        # Flag for show-status of help
        self._hide_help = True

        # Tool button for showing and hide detail help
        self.switch_button = QToolButton()
        self.switch_button.setArrowType(4)  # 2=down arrow, 4=right arrow
        # noinspection PyUnresolvedReferences
        self.switch_button.clicked.connect(self.show_hide_help)
        self.switch_button.setToolTip('Click for detail help')
        self.switch_button_stylesheet = 'border: none;'
        self.switch_button.setStyleSheet(self.switch_button_stylesheet)
        # Layouts
        self.main_layout = QVBoxLayout()
        self.input_layout = QHBoxLayout()
        self.help_layout = QGridLayout()
        # _inner_input_layout must be filled with widget in the child class
        self.inner_input_layout = QHBoxLayout()
        self.inner_help_layout = QVBoxLayout()

        # spacing
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setSpacing(0)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.help_layout.setSpacing(0)
        self.help_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_input_layout.setSpacing(7)
        self.inner_input_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_help_layout.setSpacing(0)
        self.inner_help_layout.setContentsMargins(0, 0, 0, 0)

        # Put elements into layouts
        self.input_layout.addWidget(self.label)
        self.input_layout.addLayout(self.inner_input_layout)

        if self._parameter.description:
            self.help_layout.addWidget(self.description_text_label, 0, 1)
        if self._parameter.help_text:
            self.help_layout.addWidget(self.switch_button, 0, 0)
            self.help_layout.addWidget(self.help_label, 1, 1)

        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addLayout(self.help_layout)

        self.setLayout(self.main_layout)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

    def get_parameter(self):
        """Interface for returning parameter object.

        This must be implemented in child class.

        :raises: NotImplementedError

        """
        raise NotImplementedError('Must be implemented in child class')

    def show_hide_help(self):
        """Show and hide long help."""
        if self._hide_help:
            self._hide_help = False
            self.help_label.show()
            self.switch_button.setArrowType(2)
            self.switch_button.setToolTip('Click for hide detail help')
        else:
            self._hide_help = True
            self.help_label.hide()
            self.switch_button.setArrowType(4)
            self.switch_button.setToolTip('Click for detail help')
