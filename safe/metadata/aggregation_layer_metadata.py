# coding=utf-8
"""Aggregation Layer Metadata"""

from safe.metadata.generic_layer_metadata import GenericLayerMetadata
from safe.metadata.utils import merge_dictionaries

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '4c85bcb847131a3d634744b9ea01083b158493bf'


class AggregationLayerMetadata(GenericLayerMetadata):
    """
    Metadata class for aggregation layers

    .. versionadded:: 3.2
    """

    _standard_properties = {}
    _standard_properties = merge_dictionaries(
        GenericLayerMetadata._standard_properties, _standard_properties)
