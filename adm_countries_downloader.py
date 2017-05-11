# coding=utf-8
"""OSM Downloader tool."""

import zipfile
import os
import logging
import tempfile

from PyQt4.QtNetwork import QNetworkReply
from PyQt4.QtGui import QDialog

from inasafe.utilities.i18n import tr
from inasafe.utilities.file_downloader import FileDownloader
from inasafe.common.exceptions import DownloadError, CanceledImportDialogError

# If it's not a final release and the developer mode is ON, we use the staging
# version for OSM-Reporter.

LOGGER = logging.getLogger('SaVap')


def download_country(country, output_base_path, progress_dialog=None):

    url = 'http://ims.geoinfo.ait.ac.th/countries_admin/'+country+'.zip'

    if not os.path.isdir(output_base_path):
        os.makedirs(output_base_path)

    path = output_base_path+'/'+country+'.zip'

    # download and extract it
    fetch_zip(url, path, country, progress_dialog)
    extract_zip(path,output_base_path)
    os.remove(path)

    if progress_dialog:
        progress_dialog.done(QDialog.Accepted)


def fetch_zip(url, output_path, country, progress_dialog=None):
    LOGGER.debug('Downloading file from URL: %s' % url)
    LOGGER.debug('Downloading to: %s' % output_path)

    if progress_dialog:
        progress_dialog.show()

        # Infinite progress bar when the server is fetching data.
        # The progress bar will be updated with the file size later.
        progress_dialog.setMaximum(0)
        progress_dialog.setMinimum(0)
        progress_dialog.setValue(0)

        # Get a pretty label from feature_type, but not translatable
        label_feature_type = country

        label_text = tr('Fetching %s' % label_feature_type)
        progress_dialog.setLabelText(label_text)

    # Download Process
    downloader = FileDownloader(url, output_path, progress_dialog)
    try:
        result = downloader.download()
    except IOError as ex:
        raise IOError(ex)

    if result[0] is not True:
        _, error_message = result

        if result[0] == QNetworkReply.OperationCanceledError:
            raise CanceledImportDialogError(error_message)
        else:
            raise DownloadError(error_message)


def extract_zip(zip_path,path_folder):
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(path_folder)
    zip_ref.close()
