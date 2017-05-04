# coding=utf-8
"""Metadata init file."""

# expose for nicer imports
# pylint: disable=unused-import
from inasafe.metadata.base_metadata import BaseMetadata
from inasafe.metadata.generic_layer_metadata import GenericLayerMetadata
from inasafe.metadata.exposure_summary_layer_metadata import (
    ExposureSummaryLayerMetadata)
from inasafe.metadata.exposure_layer_metadata import ExposureLayerMetadata
from inasafe.metadata.hazard_layer_metadata import HazardLayerMetadata
from inasafe.metadata.aggregation_layer_metadata import AggregationLayerMetadata
# pylint: enable=unused-import

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '4c85bcb847131a3d634744b9ea01083b158493bf'
