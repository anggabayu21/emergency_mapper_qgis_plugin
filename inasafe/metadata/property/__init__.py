# coding=utf-8
"""Property init file."""

# expose for nicer imports
# pylint: disable=unused-import
from inasafe.metadata.property.base_property import BaseProperty
from inasafe.metadata.property.character_string_property import (
    CharacterStringProperty)
from inasafe.metadata.property.date_property import DateProperty
from inasafe.metadata.property.url_property import UrlProperty
from inasafe.metadata.property.dictionary_property import DictionaryProperty
from inasafe.metadata.property.integer_property import IntegerProperty
from inasafe.metadata.property.boolean_property import BooleanProperty
from inasafe.metadata.property.float_property import FloatProperty
from inasafe.metadata.property.list_property import ListProperty
from inasafe.metadata.property.tuple_property import TupleProperty
from inasafe.metadata.property.float_tuple_property import FloatTupleProperty
# pylint: enable=unused-import

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '4c85bcb847131a3d634744b9ea01083b158493bf'
