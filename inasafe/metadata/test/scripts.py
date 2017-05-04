# coding=utf-8
"""Scripts for metadata."""

from inasafe.metadata.exposure_layer_metadata import ExposureLayerMetadata
from inasafe.metadata.hazard_layer_metadata import HazardLayerMetadata
from inasafe.metadata.aggregation_layer_metadata import AggregationLayerMetadata
from inasafe.metadata.exposure_summary_layer_metadata import \
    ExposureSummaryLayerMetadata

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '4c85bcb847131a3d634744b9ea01083b158493bf'


def print_properties():
    """Print properties from all metadata in Markdown table."""
    metadata = [
        ExposureLayerMetadata,
        HazardLayerMetadata,
        AggregationLayerMetadata,
        ExposureSummaryLayerMetadata
    ]

    for the_metadata in metadata:
        print '## ', the_metadata.__name__
        print 'No | Property | Type'
        print '------------ | ------------ | -------------'
        for i, item in enumerate(the_metadata._standard_properties.items()):
            print '%s | %s | %s' % (i + 1, item[0], item[1].split(':')[-1])
        print


if __name__ == '__main__':
    print_properties()
