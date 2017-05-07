# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaVap
                                 A QGIS plugin
 This plugin is to create a map with Sentinel Asia Value Added Product
                              -------------------
        begin                : 2017-03-22
        git sha              : 93c55caa41f16a598bbdb1893892cbb342e150cf
        copyright            : (C) 2017 by GIC - AIT
        email                : anggabayu@ait.asia
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))
#sys.path.append('/usr/share/qgis/python/plugins')

#import inasafe_extras.processing
from inasafe_extras.processing.algs.qgis import Intersection,PointsInPolygon,ZonalStatistics
from inasafe_extras.processing.core.SilentProgress import SilentProgress

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QObject, SIGNAL, SLOT, QT_VERSION, QFileInfo, QVariant, pyqtSignal
from PyQt4.QtGui import QAction, QIcon, QTableWidgetItem,QMessageBox,QHeaderView,QFont,QWidget,QTextCursor
from PyQt4.QtGui import QGraphicsScene,QPixmap,QGraphicsPixmapItem,QPainter, QAbstractItemView, QApplication, QMenu, QFileDialog, QProgressBar, QListView, QStandardItemModel, QStandardItem, QPixmap, QLabel, QColor, QProgressDialog,QTreeWidget,QCompleter,QTreeWidgetItem
from PyQt4.QtNetwork import *
from PyQt4.QtXml import QDomDocument
from qgis.gui import QgsMessageBar, QgsMapCanvas, QgsLayerTreeMapCanvasBridge,QgsMapToolPan
from qgis.core import QgsComposition, QgsApplication, QgsProviderRegistry, QgsGraduatedSymbolRendererV2, QgsSymbolV2,QgsRendererRangeV2
# Initialize Qt resources from file resources.py
import resources
import sys
import logging
import qgis

from cacheDB import cacheDB

# Import the code for the DockWidget
from sa_vap_dockwidget import SaVapDockWidget
# Import the code for the Dialog
from import_data import ImportData
from import_bm_data import ImportBMData
from basemap import Basemap
from analysis import Analysis
from print_map import PrintMap
from GreekOpenData_dialog import GreekOpenDataDialog
from select_exposure_data import SelectExposureData
from open_data_download import OpenDataDownload
from geobingan import Geobingan
from location_search import LocationSearch
from building_osm import BuildingOsm
from road_osm import RoadOsm
from country_detail_adm import CountryDetailAdm
from webService_CLASS import WebServiceParams
from wizard_quickmap_0 import WizardQuickmap0
from wizard_quickmap_1 import WizardQuickmap1
from wizard_quickmap_2 import WizardQuickmap2
from wizard_impact_0 import WizardImpact0
from wizard_impact_1 import WizardImpact1
from wizard_impact_2 import WizardImpact2

from adm_countries_downloader import download_country

from utilities import resources_path

import os.path, webbrowser,urllib,urlparse, urllib2
import csv
import xml.etree.ElementTree as ET
#from PIL import Image
from qgis.gui import *
from qgis.core import *
from os.path import basename, splitext

from inasafe.common.version import release_status
from inasafe.common.exceptions import TranslationLoadError
from inasafe.utilities.resources import resources_path
from inasafe.utilities.gis import is_raster_layer, qgis_version,viewport_geo_array,rectangle_geo_array,validate_geo_array
from inasafe.utilities.file_downloader import FileDownloader
from inasafe.gui.tools.rectangle_map_tool import RectangleMapTool
from inasafe.utilities.osm_downloader import download
from inasafe.common.exceptions import (
    CanceledImportDialogError,
    FileMissingError)
from osm_downloader_dialog import OsmDownloaderDialog

from random import randint
from time import gmtime, strftime
import time
import json

from openstreetmap.about_dialog import AboutDialog
from openstreetmap.openlayers_overview import OLOverview
from openstreetmap.openlayers_layer import OpenlayersLayer
from openstreetmap.openlayers_plugin_layer_type import OpenlayersPluginLayerType
from openstreetmap.tools_network import getProxy
from openstreetmap.weblayers.weblayer_registry import WebLayerTypeRegistry
from openstreetmap.weblayers.google_maps import OlGooglePhysicalLayer, OlGoogleStreetsLayer, OlGoogleHybridLayer, OlGoogleSatelliteLayer
from openstreetmap.weblayers.osm import OlOpenStreetMapLayer, OlOpenCycleMapLayer, OlOCMLandscapeLayer, OlOCMPublicTransportLayer, OlOSMHumanitarianDataModelLayer
from openstreetmap.weblayers.bing_maps import OlBingRoadLayer, OlBingAerialLayer, OlBingAerialLabelledLayer
from openstreetmap.weblayers.apple_maps import OlAppleiPhotoMapLayer
from openstreetmap.weblayers.osm_stamen import OlOSMStamenTonerLayer, OlOSMStamenTonerLiteLayer, OlOSMStamenWatercolorLayer, OlOSMStamenTerrainLayer
from openstreetmap.weblayers.map_quest import OlMapQuestOSMLayer, OlMapQuestOpenAerialLayer

LOGGER = logging.getLogger('SaVap')
reload(sys)
sys.setdefaultencoding("utf-8")

class SaVap:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SaVap_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Emergency Mapper')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Emergency Mapper')
        self.toolbar.setObjectName(u'Emergency Mapper')

        #print "** INITIALIZING SaVap"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Emergency Mapper', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def add_action_importdata(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        
        # Create the dialog (after translation) and keep reference
        self.import_data_dlg = ImportData()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def add_action_basemap(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        
        # Create the dialog (after translation) and keep reference
        self.basemap_dlg = Basemap()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action   

    def add_action_analysis(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        

        # Create the dialog (after translation) and keep reference
        self.analysis_dlg = Analysis()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action  

    def add_action_print(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        
        # Create the dialog (after translation) and keep reference
        self.print_dlg = PrintMap()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action  

    def add_open_data(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        
        # Create the dialog (after translation) and keep reference
        self.open_data_dlg = OpenDataDownload()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action       
          

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.canvas = self.iface.mapCanvas()
        icon_earth = resources_path('img','icon','earth.png')
        print icon_earth
        self.add_action(icon_earth,
            text=self.tr(u'Emergency Mapper Dock'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.register_basemap_layers()
        icon_basemap = resources_path('img','icon','basemap.png')
        self.add_action_basemap(icon_basemap,
            text=self.tr(u'Background Map'),
            callback=self.run_basemap,
            parent=self.iface.mainWindow())

        icon_database = resources_path('img','icon','database.png')
        self.add_action_webservice(icon_database,
            text=self.tr(u'VAP Data Collection'),
            callback=self.run_loadwebservice,
            parent=self.iface.mainWindow())

        icon_open_data = resources_path('img','icon','cloud-download.png')
        self.add_open_data(icon_open_data,
            text=self.tr(u'Download Open Data'),
            callback=self.run_opendata,
            parent=self.iface.mainWindow())

        #self._create_osm_downloader_action()

        icon_importdata = resources_path('img','icon','import_data.png')
        self.add_action_importdata(icon_importdata,
            text=self.tr(u'Import Data'),
            callback=self.run_importdata,
            parent=self.iface.mainWindow())


        icon_analysis = resources_path('img','icon','analysis.png')
        self.add_action_analysis(icon_analysis,
            text=self.tr(u'Analysis'),
            callback=self.run_analysis,
            parent=self.iface.mainWindow())

        icon_print = resources_path('img','icon','print.png')
        self.add_action_print(icon_print,
            text=self.tr(u'Print Map'),
            callback=self.run_print,
            parent=self.iface.mainWindow())

        self.geobingan_dlg = Geobingan()
        self.import_bm_data_dlg = ImportBMData()

        self.analysis_content = ""
        self.result_lbl = ""
        self.method_name_global = ""
        self.total_analysis_with_grad = ""
        self.total_affected_population = ""
        self.total_affected_building_grad = ""
        self.total_affected_building = ""
        self.total_geobingan_data = {}
        self.init_wizard()
        self.init_location_search()
        self.run()
        self.register_button()
        self.select_webservice_from = ""
    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING SaVap"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD SaVap"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&SaVap'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def register_button(self):
        self.dockwidget.wizard_button.clicked.connect(self.run_wizard_quickmap0)
        self.dockwidget.impact_analysis_button.clicked.connect(self.run_wizard_impact0)
        self.import_data_dlg.browse_file_btn.clicked.connect(self.select_file_importdata)
        self.import_data_dlg.load_import_data_btn.clicked.connect(self.load_file_importdata)
        self.import_data_dlg.cancel_import_data_btn.clicked.connect(self.close_importdata)
        self.import_data_dlg.delete_layers_btn.clicked.connect(self.delete_importdata)
        self.import_bm_data_dlg.browse_file_btn.clicked.connect(self.select_file_importbmdata)
        self.import_bm_data_dlg.load_import_data_btn.clicked.connect(self.load_file_importbmdata)
        self.import_bm_data_dlg.cancel_import_data_btn.clicked.connect(self.close_importbmdata)
        self.basemap_dlg.osm_btn.clicked.connect(lambda: self.choose_layer(0))
        self.basemap_dlg.google_street_btn.clicked.connect(lambda: self.choose_layer(1))
        self.basemap_dlg.google_hybrid_btn.clicked.connect(lambda: self.choose_layer(2))
        self.basemap_dlg.google_satellite_btn.clicked.connect(lambda: self.choose_layer(3))
        self.basemap_dlg.bing_road_btn.clicked.connect(lambda: self.choose_layer(4))
        self.basemap_dlg.bing_aerial_btn.clicked.connect(lambda: self.choose_layer(5))
        self.basemap_dlg.other_btn.clicked.connect(self.run_importbmdata)
        self.analysis_dlg.run_analysis_btn.clicked.connect(self.execute_analysis)
        self.analysis_dlg.cancel_analysis_btn.clicked.connect(self.close_analysis)
        self.print_dlg.print_btn.clicked.connect(self.export_to_pdf)
        self.print_dlg.to_jpg_btn.clicked.connect(self.export_to_jpg)
        self.print_dlg.map_composer_btn.clicked.connect(self.to_map_composer)
        self.print_dlg.cancel_btn.clicked.connect(self.close_print)
        self.print_dlg.directory_button.clicked.connect(self.select_dir_map)
        self.open_data_dlg.osm_btn.clicked.connect(self.od_osm_downloader_click)
        self.open_data_dlg.geoBingAn_btn.clicked.connect(self.od_geobingan_click)
        self.open_data_dlg.cancel_btn.clicked.connect(self.close_open_data)
        self.geobingan_dlg.download_btn.clicked.connect(self.geobingan_download_click)
        self.geobingan_dlg.cancel_btn.clicked.connect(self.close_geobingan)     
        self.wizard_quickmap0_dlg.next_btn.clicked.connect(self.run_wizard_quickmap1)
        self.wizard_quickmap0_dlg.location_search_btn.clicked.connect(self.run_location_search)
        self.wizard_quickmap0_dlg.cancel_btn.clicked.connect(self.close_wizard_quickmap0)
        self.wizard_quickmap0_dlg.country_comboBox.currentIndexChanged.connect(lambda: self.country_extend1(self.wizard_quickmap0_dlg.country_comboBox.currentText()))
        self.wizard_quickmap1_dlg.next_btn.clicked.connect(self.run_wizard_quickmap2)
        self.wizard_quickmap1_dlg.back_btn.clicked.connect(self.back_wizard_quickmap1)
        self.wizard_quickmap1_dlg.basemap_btn.clicked.connect(self.run_basemap)
        self.wizard_quickmap1_dlg.vap_btn.clicked.connect(lambda: self.run_loadwebservice('quickmap'))
        self.wizard_quickmap1_dlg.osm_btn.clicked.connect(self.show_building_osm)
        self.wizard_quickmap1_dlg.osm_road_btn.clicked.connect(self.show_road_osm)
        self.wizard_quickmap1_dlg.geobingan_btn.clicked.connect(self.geobingan_download_click)
        self.wizard_quickmap1_dlg.local_btn.clicked.connect(self.run_importdata)
        self.wizard_quickmap1_dlg.delete_layers_btn.clicked.connect(self.wiz_delete_layers_btn_click)
        self.wizard_quickmap2_dlg.back_btn.clicked.connect(self.back_wizard_quickmap2)
        self.wizard_quickmap2_dlg.export_btn.clicked.connect(self.run_print)
        self.wizard_quickmap2_dlg.next_btn.clicked.connect(self.close_wizard_quickmap2)
        self.wizard_quickmap2_dlg.delete_layers_btn.clicked.connect(self.wiz_delete1_layers_btn_click)
        self.wizard_impact0_dlg.next_btn.clicked.connect(self.run_wizard_impact1)
        self.wizard_impact0_dlg.cancel_btn.clicked.connect(self.close_wizard_impact0)
        self.wizard_impact0_dlg.select_country_admin_btn.clicked.connect(self.run_country_detail_adm)
        self.wizard_impact0_dlg.country_comboBox.currentIndexChanged.connect(lambda: self.country_extend1(self.wizard_impact0_dlg.country_comboBox.currentText()))
        self.wizard_impact1_dlg.next_btn.clicked.connect(self.run_wizard_impact2)
        self.wizard_impact1_dlg.back_btn.clicked.connect(self.back_wizard_impact1)
        self.wizard_impact1_dlg.basemap_btn.clicked.connect(self.run_basemap)
        self.wizard_impact1_dlg.vap_btn.clicked.connect(lambda: self.run_loadwebservice('impactmap'))
        self.wizard_impact1_dlg.osm_btn.clicked.connect(self.select_analysis_data)
        self.wizard_impact1_dlg.geobingan_btn.clicked.connect(self.run_geobingan)
        self.wizard_impact1_dlg.local_btn.clicked.connect(self.run_importdata)
        self.wizard_impact1_dlg.delete_layers_btn.clicked.connect(self.wiz1_delete_layers_btn_click)
        self.wizard_impact1_dlg.run_analysis_btn.clicked.connect(self.run_wizard_analysis)
        self.wizard_impact2_dlg.back_btn.clicked.connect(self.back_wizard_impact2)
        self.wizard_impact2_dlg.export_btn.clicked.connect(self.run_print)
        self.wizard_impact2_dlg.next_btn.clicked.connect(self.close_wizard_impact2)
        self.wizard_impact2_dlg.delete_layers_btn.clicked.connect(self.wiz1_delete1_layers_btn_click)
        self.select_exposure_data_dlg.osm_btn.clicked.connect(self.wiz_osm_downloader_click)
        self.select_exposure_data_dlg.import_data_btn.clicked.connect(self.wiz_import_data_click)
        self.select_exposure_data_dlg.cancel_btn.clicked.connect(self.close_select_exposure_data)
        self.location_search_dlg.capture_button.clicked.connect(self.drag_rectangle_on_map_canvas)
        self.location_search_dlg.ok_btn.clicked.connect(self.close_location_search)
        self.building_osm_dlg.ok_btn.clicked.connect(self.load_file_building)
        self.building_osm_dlg.cancel_btn.clicked.connect(self.close_building_osm)
        self.building_osm_dlg.browse_file_btn.clicked.connect(self.select_file_building)
        self.building_osm_dlg.osm_radio.clicked.connect(self.radio_building_click)
        self.building_osm_dlg.local_radio.clicked.connect(self.radio_building_click)
        self.building_osm_dlg.directory_button.clicked.connect(self.building_dir_map)
        self.road_osm_dlg.ok_btn.clicked.connect(self.load_file_road)
        self.road_osm_dlg.cancel_btn.clicked.connect(self.close_road_osm)
        self.road_osm_dlg.browse_file_btn.clicked.connect(self.select_file_road)
        self.road_osm_dlg.osm_radio.clicked.connect(self.radio_road_click)
        self.road_osm_dlg.local_radio.clicked.connect(self.radio_road_click)
        self.road_osm_dlg.directory_button.clicked.connect(self.road_dir_map)
        self.country_detail_adm_dlg.ok_btn.clicked.connect(self.load_country_adm)
        self.country_detail_adm_dlg.cancel_btn.clicked.connect(self.close_country_detail_adm)
        self.country_detail_adm_dlg.download_button.clicked.connect(self.country_adm_download_button_click)

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING SaVap"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = SaVapDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

            pixmap = QPixmap(resources_path('img','adb.png'))
            self.dockwidget.organisation_logo.setPixmap(pixmap)
            self.dockwidget.organisation_logo.show()

            pixmap2 = QPixmap(resources_path('img','sentinel_asia.png'))
            self.dockwidget.organisation_logo_2.setPixmap(pixmap2)
            self.dockwidget.organisation_logo_2.show()

    def run_importdata(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.import_data_dlg.show()
        self.import_data_dlg.file_path_lineedit.setText('')
        self.import_data_list = []
        
    def run_importbmdata(self):
        self.import_bm_data_dlg.show()
        self.import_bm_data_dlg.file_path_lineedit.setText('')    

    def select_file_importdata(self):
        #if self.file_importdata_clicked:
        filepath = QFileDialog.getOpenFileName()
        self.import_data_dlg.file_path_lineedit.setText(filepath) 
        if self.import_data_dlg.file_path_lineedit.text() != "":
            self.import_data_list.append(self.import_data_dlg.file_path_lineedit.text())
            self.update_import_data_listView()
        
    def update_import_data_listView(self):  
        list = self.import_data_dlg.layers_listView
        self.model_import = QStandardItemModel(list)
         
        for data in self.import_data_list:
            # create an item with a caption
            item = QStandardItem(data)
            # add a checkbox to it
            item.setCheckable(True)
            # Add the item to the model
            self.model_import.appendRow(item)
        # Apply the model to the list view
        list.setModel(self.model_import)  

    def delete_importdata(self):
        import_data_list = []
        i = 0
        for data in self.import_data_list:
            if self.model_import.item(i).checkState() != 2:
                import_data_list.append(data)
            i += 1 
        self.import_data_list = import_data_list
        self.update_import_data_listView()

    def load_file_importdata(self):    
        #if self.load_importdata_clicked:
            #self.load_importdata_clicked = False
        failed_import_file = "" 
        header_failed_msg = "This file(s) failed to import"   
        for data in self.import_data_list:    
            filepath = data
            extention_file = splitext(basename(filepath))[1]
            filename = splitext(basename(filepath))[0]
            if extention_file == ".shp" or extention_file == ".geojson" or extention_file == ".kml":
                layer = self.iface.addVectorLayer(filepath, filename, "ogr")
            elif extention_file == ".tif":    
                layer = self.iface.addRasterLayer(filepath, filename)
            else:
                failed_import_file = failed_import_file + ", " + filename
                #QMessageBox.information(None, "Error:", str("Only shapefile, geojson, kml and tiff file is allowed"))
                
        if failed_import_file != "":
            failed_import_file = header_failed_msg + failed_import_file
            QMessageBox.information(None, "Error:", failed_import_file)
    
        self.import_data_dlg.close()  
        if self.wizard_clicked:
            self.wizard_quickmap_trigger()
        if self.wizard1_clicked:
            self.wizard_impact_trigger()    

    def close_importdata(self):
        self.import_data_dlg.close()   

    def select_file_importbmdata(self):
        filepath = QFileDialog.getOpenFileName()
        self.import_bm_data_dlg.file_path_lineedit.setText(filepath) 

    def load_file_importbmdata(self):    
        filepath = self.import_bm_data_dlg.file_path_lineedit.text()
        extention_file = splitext(basename(filepath))[1]
        filename = splitext(basename(filepath))[0]
        if extention_file == ".shp" or extention_file == ".geojson" or extention_file == ".kml":
            layer = self.iface.addVectorLayer(filepath, filename, "ogr")
        elif extention_file == ".tif":    
            layer = self.iface.addRasterLayer(filepath, filename)
        else:
            QMessageBox.information(None, "Error:", str("Only shapefile, geojson, kml and tiff file is allowed"))
            
        if not layer:
            QMessageBox.information(None, "Error:", str("Only shapefile, geojson, kml and tiff file is allowed"))
        else:
            self.import_bm_data_dlg.close()
            self.basemap_dlg.close()  
            if self.wizard_clicked:
                self.wizard_quickmap_trigger()
            if self.wizard1_clicked:
                self.wizard_impact_trigger()    

    def close_importbmdata(self):
        self.import_bm_data_dlg.close()              

    def run_basemap(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.basemap_dlg.show()
        self.wiz_basemap_clicked = False
        # Run the dialog event loop
        result = self.basemap_dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass        
             
    def choose_layer(self,layer_id):
        layer = self._olLayerTypeRegistry.getById(layer_id)
        layer.addLayer() 
        self.basemap_dlg.close()  
        if self.wizard_clicked:
            self.wizard_quickmap_trigger()
        if self.wizard1_clicked:
            self.wizard_impact_trigger()    

    def run_analysis(self):
        """Run method that performs all the real work"""
        layers = self.iface.legendInterface().layers()
        self.analysis_dlg.hazard_layer_comboBox.clear()
        self.analysis_dlg.exposure_layer_comboBox.clear()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        if len(layer_list) > 0:        
            self.analysis_dlg.hazard_layer_comboBox.addItems(layer_list)
            self.analysis_dlg.exposure_layer_comboBox.addItems(layer_list)
        # show the dialog
        self.analysis_dlg.show() 
        self.execute_analysis_clicked = True
        
    def close_analysis(self):
        self.analysis_dlg.close()                               

    def register_basemap_layers(self):
        self._olLayerTypeRegistry = WebLayerTypeRegistry(self)

        self._olLayerTypeRegistry.register(OlOpenStreetMapLayer())
        self._olLayerTypeRegistry.register(OlGoogleStreetsLayer())
        self._olLayerTypeRegistry.register(OlGoogleHybridLayer())
        self._olLayerTypeRegistry.register(OlGoogleSatelliteLayer())
        self._olLayerTypeRegistry.register(OlBingRoadLayer())
        self._olLayerTypeRegistry.register(OlBingAerialLayer())

        self._olLayerTypeRegistry.register(OlOpenCycleMapLayer())
        self._olLayerTypeRegistry.register(OlOCMLandscapeLayer())
        self._olLayerTypeRegistry.register(OlOCMPublicTransportLayer())
        self._olLayerTypeRegistry.register(OlOSMHumanitarianDataModelLayer())
        self._olLayerTypeRegistry.register(OlGooglePhysicalLayer())
        self._olLayerTypeRegistry.register(OlBingAerialLabelledLayer())
        
        # Register plugin layer type
        self.pluginLayerType = OpenlayersPluginLayerType(self.iface, self.setReferenceLayer,
                                                    self._olLayerTypeRegistry)
        QgsPluginLayerRegistry.instance().addPluginLayerType(self.pluginLayerType)
        self.setGDALProxy()

    #SAFE - OSM Downloader 
    def _create_osm_downloader_action(self):
        """Create action for import OSM Dialog."""
        icon = resources_path('img', 'icon', 'osm.png')
        self.action_import_dialog = QAction(
            QIcon(icon),
            self.tr('OpenStreetMap Downloader'),
            self.iface.mainWindow())
        self.action_import_dialog.setStatusTip(self.tr(
            'OpenStreetMap Downloader'))
        self.action_import_dialog.setWhatsThis(self.tr(
            'OpenStreetMap Downloader'))
        self.action_import_dialog.triggered.connect(self.show_osm_downloader)
        self.add_action_safe(self.action_import_dialog)

    def show_osm_downloader(self, method_name=''):
        """Show the OSM buildings downloader dialog."""
        dialog = OsmDownloaderDialog(self.iface.mainWindow(), self.iface, self.callbackclose)
        dialog.show()  # non modal
        if method_name == 'impactmap':
            dialog.roads_flag.setDisabled(True)
            dialog.buildings_flag.setDisabled(True)
        else:
            dialog.roads_flag.setDisabled(False)
            dialog.buildings_flag.setDisabled(False)

    def add_action_safe(self, action, add_to_toolbar=True, add_to_legend=False):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param action: The action that should be added to the toolbar.
        :type action: QAction

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the InaSAFE toolbar. Defaults to True.
        :type add_to_toolbar: bool

        """
        # store in the class list of actions for easy plugin unloading
        self.actions.append(action)
        self.iface.addPluginToMenu(self.menu, action)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_legend:
            # The id is the action name without spaces, tabs ...
            self.iface.legendInterface().addLegendLayerAction(
                action,
                self.tr('SaVap'),
                ''.join(action.text().split()),
                QgsMapLayer.VectorLayer,
                True)
            self.iface.legendInterface().addLegendLayerAction(
                action,
                self.tr('SaVap'),
                ''.join(action.text().split()),
                QgsMapLayer.RasterLayer,
                True)

    def callbackclose(self): 
        if self.wizard_clicked:
            self.wizard_quickmap_trigger()
            self.wizard_quickmap1_dlg.close()
            self.wizard_quickmap1_dlg.show()
        if self.wizard1_clicked:
            self.wizard_impact_trigger()  
            self.wizard_impact1_dlg.close()  
            self.wizard_impact1_dlg.show()  
                      
    #Open Data Webservice
    def add_action_webservice(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        # Create the dialog (after translation) and keep reference
        self.dlg = GreekOpenDataDialog()
        self.language = "EN"  #start language
        self.csvWithDatasets = os.path.join(os.path.dirname(__file__),"data/webservice/data.csv")
        self.quicklooks_dir =  os.path.join(os.path.dirname(__file__),"data/webservice/quicklooks")
        # define the datasets used. List of webServices custon objects
        if os.path.exists(resources_path('webservice', 'getcapabilities_wfs.xml')) == False:
            self.download_xml_wfs() 
        if os.path.exists(resources_path('webservice', 'getcapabilities_wms.xml')) == False:
            self.download_xml_wms()
        if os.path.exists(resources_path('webservice', 'getcapabilities_wcs.xml')) == False:
            self.download_xml_wcs()         
            
        self.datasets = self.loadDataSetsXMLWMSWFS()
        self.datasets_temp = self.datasets

        #events        
        self.dlg.tableWidget.itemSelectionChanged.connect(self.updateDescAndQL)
        self.dlg.load_btn.released.connect(self.loadWebService)
        self.dlg.close_btn.released.connect(self.closeWebService)   
        self.dlg.refresh_data_btn.released.connect(self.refresh_data_wmswfs)     
        self.init_table()     
        self.dlg.search_lineEdit.textEdited.connect(self.search)     

        icon = QIcon(icon_path)
        action = QAction(icon, "Value Added Product Data", parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis("Value Added Product Data" )

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def refresh_data_wmswfs(self):
        self.download_xml_wms()
        self.download_xml_wfs()
        self.download_xml_wcs()  
        self.datasets = self.loadDataSetsXMLWMSWFS()
        self.datasets_temp = self.datasets

        if self.method_name_global == 'quickmap':
            self.filter_data_quickmap()
        elif self.method_name_global == 'impactmap':
            self.filter_data_impactmap('VAP')
        elif self.method_name_global == 'impactmap1':
            self.filter_data_impactmap('Population')       
        else:    
            self.init_table()        

    def download_xml_wms(self):
        url = "http://ims.geoinfo.ait.ac.th:8090/geoserver/sentinel/wms?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetCapabilities"
        s = urllib2.urlopen(url)
        contents = s.read()
        file = open(resources_path('webservice', 'getcapabilities_wms.xml'), 'w')
        file.write(contents)
        file.close()  
        #self.datasets = self.loadDataSetsXMLWMS()

    def download_xml_wfs(self):
        url = "http://ims.geoinfo.ait.ac.th:8090/geoserver/sentinel/wfs?SERVICE=WFS&VERSION=1.1.1&REQUEST=GetCapabilities"
        s = urllib2.urlopen(url)
        contents = s.read()
        file = open(resources_path('webservice', 'getcapabilities_wfs.xml'), 'w')
        file.write(contents)
        file.close()  
        #self.datasets = self.loadDataSetsXMLWFS()   

    def download_xml_wcs(self):
        url = "http://ims.geoinfo.ait.ac.th:8090/geoserver/sentinel/wcs?service=WCS&version=1.1.0&request=GetCapabilities"
        s = urllib2.urlopen(url)
        contents = s.read()
        file = open(resources_path('webservice', 'getcapabilities_wcs.xml'), 'w')
        file.write(contents)
        file.close()

    def download_wcs_tiff(self,url,layer_name,output_path):
        self.progress_dialog = QProgressDialog()
        self.progress_dialog.setAutoClose(False)
        title = self.tr(layer_name+' Download')
        self.progress_dialog.setWindowTitle(title)

        if self.progress_dialog:
            self.progress_dialog.show()

            # Infinite progress bar when the server is fetching data.
            # The progress bar will be updated with the file size later.
            self.progress_dialog.setMaximum(0)
            self.progress_dialog.setMinimum(0)
            self.progress_dialog.setValue(0)

            # Get a pretty label from feature_type, but not translatable
            label_feature_type = layer_name

            label_text = self.tr('Fetching %s' % label_feature_type)
            self.progress_dialog.setLabelText(label_text)

        # Download Process
        downloader = FileDownloader(url, output_path, self.progress_dialog)
        try:
            result = downloader.download()
        except IOError as ex:
            raise IOError(ex)

        if result[0] is not True:
            _, error_message = result

            if result[0] == QNetworkReply.OperationCanceledError:
                #raise CanceledImportDialogError(error_message)
                pass
            else:
                #raise DownloadError(error_message)  
                pass

        if self.progress_dialog:
            self.progress_dialog.close()           

    def getSelectedNameAndType(self):
        """Gets the name and servive type of the selected dataset."""
        # get the selected row (list with indices)
        try:
            selectedIndexes = self.dlg.tableWidget.selectionModel().selectedRows()            
            row = selectedIndexes[0].row()
        except IOError as ex:
            raise IOError(ex)    

        # get name and service typeof selected row
        dataset_name = self.dlg.tableWidget.item(row, 0).text()
        dataset_serviceType = self.dlg.tableWidget.item(row, 5).text()
        #dataset_name = unicode(dataset_name, 'utf-8')
        return [dataset_name,dataset_serviceType]

    def loadDataSetsXMLWMSWFS(self):
        webServicesList = []
        rownum = 0

        root = ET.parse(resources_path('webservice', 'getcapabilities_wms.xml')).getroot()
        for capability in root.findall('Capability'):
            for layers in capability.findall('Layer'):
                for layer in layers.findall('Layer'):
                    nameGr = ''
                    nameEn = layer.find('Name').text
                    name = nameEn
                    sourceGR = ''
                    sourceEN = 'Geoinformatics Center - Asian Institute of Technology'
                    creationDate = ''
                    lastUpdate = ''
                    QLname = layer.find('Name').text
                    descEN = ''
                    descGR = ''
                    serviceType = 'WMS'
                    layerName = layer.find('Name').text
                    server = 'http://ims.geoinfo.ait.ac.th:8090/geoserver/sentinel/wms'
                    crc = layer.find('SRS').text

                    country=''
                    city=''
                    mapType=''
                    typeDisaster=''
                    mapFormat='Web Service'
                    for keywords in layer.findall('KeywordList'):
                        for keyword in keywords.findall('Keyword'):
                            str_keyword = keyword.text
                            if str_keyword.find('country:') > -1:
                                country = str_keyword.replace('country:','')
                            elif str_keyword.find('city:') > -1:
                                city = str_keyword.replace('city:','')    
                            elif str_keyword.find('mapType:') > -1:
                                mapType = str_keyword.replace('mapType:','')
                            elif str_keyword.find('typeDisaster:') > -1:
                                typeDisaster = str_keyword.replace('typeDisaster:','')        

                    webServiceObj = WebServiceParams(name, nameGr,nameEn,sourceGR,sourceEN,creationDate,lastUpdate,
                                                     descEN,descGR,serviceType, layerName,server,QLname,crc,'',country,city,mapType,typeDisaster,mapFormat)
                    webServicesList.append(webServiceObj)
                    print 'no error'
        rownum = 0
        root = ET.parse(resources_path('webservice', 'getcapabilities_wfs.xml')).getroot()
        i = 1
        for layers in root.findall('{http://www.opengis.net/wfs}FeatureTypeList'):
            
            for layer in layers.findall('{http://www.opengis.net/wfs}FeatureType'):
                
                nameGr = ''
                nameEn = root[3][i][1].text
                name = nameEn
                sourceGR = ''
                sourceEN = 'Geoinformatics Center - Asian Institute of Technology'
                creationDate = ''
                lastUpdate = ''
                QLname = root[3][i][0].text
                descEN = ''
                descGR = ''
                serviceType = 'WFS'
                layerName = root[3][i][0].text
                server = 'http://ims.geoinfo.ait.ac.th:8090/geoserver/sentinel/wfs'
                crc = root[3][i][4].text
                crc = crc.replace("urn:x-ogc:def:crs:","")

                country=''
                city=''
                mapType=''
                typeDisaster=''
                mapFormat='Vector'
                j = 0
                for keywords in layer.findall(root[3][i][3].tag):
                    for keyword in keywords.findall(root[3][i][3][0].tag):    
                        str_keyword = root[3][i][3][j].text
                        if str_keyword.find('country:') > -1:
                            country = str_keyword.replace('country:','')
                        elif str_keyword.find('city:') > -1:
                            city = str_keyword.replace('city:','')    
                        elif str_keyword.find('mapType:') > -1:
                            mapType = str_keyword.replace('mapType:','')
                        elif str_keyword.find('typeDisaster:') > -1:
                            typeDisaster = str_keyword.replace('typeDisaster:','')
                        j += 1       

                webServiceObj = WebServiceParams(name, nameGr,nameEn,sourceGR,sourceEN,creationDate,lastUpdate,
                                                 descEN,descGR,serviceType, layerName,server,QLname,crc,'',country,city,mapType,typeDisaster,mapFormat)
                webServicesList.append(webServiceObj)
                i = i+1

        rownum = 0
        root = ET.parse(resources_path('webservice', 'getcapabilities_wcs.xml')).getroot()
        i = 0
        #print root[3].tag #{http://www.opengis.net/ows/1.1}ServiceIdentification
        
        for layers in root.findall('{http://www.opengis.net/wcs/1.1.1}Contents'):
            
            for layer in layers.findall('{http://www.opengis.net/wcs/1.1.1}CoverageSummary'):
                
                nameGr = ''
                nameEn = root[3][i][0].text
                name = nameEn
                sourceGR = ''
                sourceEN = 'Geoinformatics Center - Asian Institute of Technology'
                creationDate = ''
                lastUpdate = ''
                QLname = root[3][i][4].text
                descEN = ''
                descGR = ''
                serviceType = 'WCS'
                layerName = root[3][i][4].text
                server = 'http://ims.geoinfo.ait.ac.th:8090/geoserver/sentinel/wcs'
                crc = "EPSG:4326"
                bbox1 = root[3][i][3][0].text
                bbox1 = bbox1.replace(' ',',')
                bbox2 = root[3][i][3][1].text
                bbox2 = bbox2.replace(' ',',')
                bbox = bbox1+','+bbox2

                country=''
                city=''
                mapType=''
                typeDisaster=''
                mapFormat='Raster'
                j = 0
                for keywords in layer.findall(root[3][i][2].tag):
                    for keyword in keywords.findall(root[3][i][2][0].tag):
                        str_keyword = root[3][i][2][j].text
                        if str_keyword.find('country:') > -1:
                            country = str_keyword.replace('country:','')
                        elif str_keyword.find('city:') > -1:
                            city = str_keyword.replace('city:','')    
                        elif str_keyword.find('mapType:') > -1:
                            mapType = str_keyword.replace('mapType:','')
                        elif str_keyword.find('typeDisaster:') > -1:
                            typeDisaster = str_keyword.replace('typeDisaster:','') 
                        j += 1      

                webServiceObj = WebServiceParams(name, nameGr,nameEn,sourceGR,sourceEN,creationDate,lastUpdate,
                                                 descEN,descGR,serviceType, layerName,server,QLname,crc,bbox,country,city,mapType,typeDisaster,mapFormat)
                webServicesList.append(webServiceObj)
                i = i+1        
        
        return webServicesList         

    def loadDatasets(self):
        f = open(self.csvWithDatasets, "rb")
        reader = csv.reader(f)       
        
        webServicesList = []
        rownum = 0
        for row in reader:
            #make sure we exclude the header
            if rownum!=0:
                nameGr = row[1]
                nameEn = row[3]
                name = nameEn
                sourceGR = row[2]
                sourceEN = row[4]
                creationDate = row[6]
                lastUpdate = row[5]
                QLname = row[7]
                descEN = row[8]
                descGR = row[9]
                serviceType = row[10]
                layerName = row[11]
                server = row[12]
                crc = "EPSG:2100"

                webServiceObj = WebServiceParams(name, nameGr,nameEn,sourceGR,sourceEN,creationDate,lastUpdate,
                                                 descEN,descGR,serviceType, layerName,server,QLname,crc,'','','','','','')
                         

                webServicesList.append(webServiceObj)
            rownum = rownum + 1
                
        f.close()
        return webServicesList
        
        
    def updateDescAndQL(self):
        # get the name of the selected dataset
        dataset_name, dataset_serviceType = self.getSelectedNameAndType()        

        #custom web service object
        dataset = self.selectdataSets(dataset_name,dataset_serviceType)        

        quicklook = os.path.join(self.quicklooks_dir, dataset.QLname+".jpg")
        desc = dataset.getDescription(self.language)
        name = dataset.getName(self.language)

        #update decription
        self.dlg.textEdit.clear()       
        #creation and last update
        
        crDate = "Creation date : "+dataset.creationDate 
        update = "Last update : "+dataset.lastUpdate            
    
        cursor = QTextCursor(self.dlg.textEdit.document())
        cursor.insertHtml("<h3> "+name+" <br><br></h3>")
        cursor.insertHtml("<p> "+desc+" <br><br><br></p>")
        cursor.insertHtml("<p><i> "+crDate+" <br></i></p>")
        #cursor.insertHtml("<p><i> "+update+" <br></i></p>")

        self.dlg.textEdit.setReadOnly(True) 
        

    def selectdataSets(self, dataset_name, dataset_serviceType):

        for dataset in self.datasets:
            # get the names both in Green and in English in UTF-8 encoding
            dataset_nameGR = unicode(dataset.nameGr, 'utf-8')
            dataset_nameEN = unicode(dataset.nameEn, 'utf-8')
            # check which dataset has the name we are looking for 
            if dataset_name == dataset_nameGR or dataset_name == dataset_nameEN:
                if dataset_serviceType == dataset.serviceType:
                    selectedDataset = dataset
                    break
        
        return selectedDataset

    def setTableWidgetBehavour(self):

        #set rows and columns default sizze and lock it       

        self.dlg.tableWidget.setColumnWidth(0,200)
        self.dlg.tableWidget.setColumnWidth(1,120)
        self.dlg.tableWidget.setColumnWidth(2,120)
        self.dlg.tableWidget.setColumnWidth(3,120)
        self.dlg.tableWidget.setColumnWidth(4,60)
        self.dlg.tableWidget.setColumnWidth(5,45)
        self.dlg.tableWidget.setColumnWidth(6,358)
        self.dlg.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Fixed)
        self.dlg.tableWidget.verticalHeader().setResizeMode(QHeaderView.Fixed)        
        
        self.dlg.tableWidget.resizeRowsToContents() 
        
        # qtableWidget behavour
        self.dlg.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dlg.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
    def fill_table(self,datasetsList):
         # first delete all elements of table        
        self.dlg.tableWidget.setRowCount(0)
        self.dlg.tableWidget.setColumnCount(7)

                        
        #FILL THE TABLE WIDGET
        # get a sorted version of lirt with WebServiceObjects
        WebServiceObjects = self.sort(datasetsList)
    
        for dataset in WebServiceObjects:
            index = WebServiceObjects.index(dataset)
            self.dlg.tableWidget.insertRow(index)            
        # fill layer name
            self.dlg.tableWidget.setItem(index , 0, QTableWidgetItem(dataset.getName(self.language))) #dataset name
            self.dlg.tableWidget.setItem(index , 1, QTableWidgetItem(dataset.mapType)) # mapType
            self.dlg.tableWidget.setItem(index , 2, QTableWidgetItem(dataset.typeDisaster)) # typeDisaster
            self.dlg.tableWidget.setItem(index , 3, QTableWidgetItem(dataset.country)) # country
            self.dlg.tableWidget.setItem(index , 4, QTableWidgetItem(dataset.mapFormat)) # mapFormat
            self.dlg.tableWidget.setItem(index , 5, QTableWidgetItem(dataset.serviceType)) # webservice type
            self.dlg.tableWidget.setItem(index , 6, QTableWidgetItem(dataset.getSource(self.language))) # source organization

        #name of columns
        self.dlg.tableWidget.setHorizontalHeaderLabels(["Name","Map","Disaster","Country","Format","Type","Organization"])
        
        self.setTableWidgetBehavour() 
        

    def init_table(self):
        # fille the table with the entire dataset collection
        self.fill_table(self.datasets)

    def init_searchBox(self):
        font = self.dlg.search_lineEdit.font()
        font.setItalic(True)
        self.dlg.search_lineEdit.setFont(font)
##        self.dlg.search_lineEdit.setFont(font)
        # welcome text
        #self.dlg.search_lineEdit.setText("Search for dataset name, service type or organization...")
        
        
    def search(self):
        # first set/change the  font of the serach box
        font = self.dlg.search_lineEdit.font()
        font.setItalic(False)
        self.dlg.search_lineEdit.setFont(font)

        # clear description and quicklook
        self.dlg.textEdit.clear()
        
        # function the searches for a string in the datasets name, service type and otganization
        text = self.dlg.search_lineEdit.text()        
        # convert to lower case and remove greek accents in case of Greek
        text = text.lower()
        text = self.removeGreekAccents(text)  
        foundDatasets = []
        for dataset in self.datasets:
            # use lowercase characters and remove greek accents , to make the comparison
            name = self.removeGreekAccents(dataset.getName(self.language).lower())
            source = self.removeGreekAccents(dataset.getSource(self.language).lower())
            serviceType = self.removeGreekAccents(dataset.serviceType.lower())
            country = dataset.country.lower()
            disasterType = dataset.typeDisaster.lower()
            
            if text in name or text in source or text in serviceType or text in country or text in disasterType:            
            #QMessageBox.information(None, "DEBUG:", str(type(dataset.getName(self.language))))                           
                foundDatasets.append(dataset)
        #fill the table with the found datasets
        self.fill_table(foundDatasets)     

    def sort(self,listOfWebServiceObj):
        """Sorts the datasets by name."""
        # make new list of list[name, obj) and sort it
        sortedList = []
        for WebServiceObj in listOfWebServiceObj:
            name = WebServiceObj.getName(self.language)
            # convert to lowercase and remove Greek accents to order properly
            name = name.lower()
            name = self.removeGreekAccents(name)     
            
            sortedList.append([name,WebServiceObj])
        sortedList.sort()
        #build the output list (only with the WebServiceObj)
        outputList = []
        for element in sortedList:
            outputList.append(element[1])       

        return outputList

    def removeGreekAccents(self,utext):
        #function to removes the Greek accents from a unicode lowercase string           
        if "ά" in utext:
            #SQMessageBox.information(None, "DEBUG:", str("removeGreekAccents condition reached"))
            utext = utext.replace("ά","α")
        if "έ" in utext:
            utext = utext.replace("έ","ε")
        if "ή" in utext:
            utext = utext.replace("ή","η")
        if "ί" in utext:
            utext = utext.replace("ί","ι")
        if "ό" in utext:
            utext = utext.replace("ό","ο")
        if "ύ" in utext:
            utext = utext.replace("ύ","υ")
        if "ώ" in utext:
            utext = utext.replace("ώ","ω")        
               
        return utext
            
    def loadWebService(self):
        # get the selected row
        dataset_name,dataset_serviceType = self.getSelectedNameAndType()        
        #custom web service object
        dataset = self.selectdataSets(dataset_name,dataset_serviceType)  
        set_extent = True      
        if self.wizard1_clicked:
            set_extent = False
                
        urlWithParams = dataset.webServiceParams()  
        print urlWithParams     
        if dataset.serviceType== "WMS":
            rlayer = QgsRasterLayer(dataset.webServiceParams(), dataset.getName(self.language), dataset.serviceType.lower())            
            if not rlayer.isValid():
                QMessageBox.information(None, "ERROR:", str("..Oops! " + dataset_name + "  cannot be loaded. Either the server is down or you have limited internet connectivity"))
                return
            QgsMapLayerRegistry.instance().addMapLayer(rlayer)                        
            self.iface.legendInterface().setLayerExpanded(rlayer,False) # collapse the layer'slegend
            self.change_canvas_proj(rlayer.crs().authid())
            canvas = self.iface.mapCanvas()
            extent = rlayer.extent()
            if set_extent:
                canvas.setExtent(extent)
                canvas.refresh()
        elif dataset.serviceType== "WFS":                       
            vlayer = QgsVectorLayer(dataset.webServiceParams(), dataset.getName(self.language), dataset.serviceType)
            #QMessageBox.information(None, "ERROR:", str(dataset.webServiceParams())) 
            if not vlayer.isValid():
                QMessageBox.information(None, "ERROR:", str("..Oops! " + dataset_name + "  cannot be loaded. Either the server is down or you have limited internet connectivity"))
                return
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            #re-appear window
            self.dlg.raise_()
            self.dlg.activateWindow()
            self.change_canvas_proj(vlayer.crs().authid())
            canvas = self.iface.mapCanvas()
            extent = vlayer.extent()
            if set_extent:
                canvas.setExtent(extent)
                canvas.refresh()
        elif dataset.serviceType== "WCS":
            output_path = resources_path('webservice', 'data.tif')
            self.download_wcs_tiff(urlWithParams,dataset_name,output_path)
            rlayer = self.iface.addRasterLayer(output_path,dataset_name)
            self.change_canvas_proj(rlayer.crs().authid())
            canvas = self.iface.mapCanvas()
            extent = rlayer.extent()
            if set_extent:
                canvas.setExtent(extent)
                canvas.refresh()   
        if self.select_webservice_from == "VAP":
            self.check_impact_layer("VAP",dataset_name)
        elif self.select_webservice_from == "Population":
            self.check_impact_layer("Population",dataset_name)  

        self.select_webservice_from = ""     
        self.closeWebService()    

    def showInfo(self):
        info_html = "info_en.html"
        # show htmpl in browser
        
        local_path = os.path.join(self.plugin_dir,info_html)        
        abs_path = os.path.abspath(local_path)       
        url = urlparse.urljoin('file:', urllib.pathname2url(abs_path))         
        #QMessageBox.information(None, "ERROR:", str(url))
        webbrowser.open_new_tab(url)


    def run_loadwebservice(self,method_name=''):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()

        self.method_name_global = method_name

        if method_name == False and self.wizard_clicked == True:
            self.datasets = self.datasets_temp
            self.fill_table(self.datasets) 

        if method_name == False and self.wizard1_clicked == True:
            self.datasets = self.datasets_temp
            self.fill_table(self.datasets)        

        self.select_webservice_from = ""
        if method_name == 'quickmap':
            self.filter_data_quickmap()
            self.select_webservice_from = ""
        elif method_name == 'impactmap':
            self.filter_data_impactmap('VAP') 
            self.select_webservice_from = "VAP"
        elif method_name == 'impactmap1':
            self.filter_data_impactmap('Population') 
            self.select_webservice_from = "Population"      

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def closeWebService(self):
        #clear everything
        self.init_table()
        # clear description and quicklook
        self.dlg.textEdit.clear()
        # clear search box
        #text = self.dlg.search_lineEdit.setText("")
        self.init_searchBox()
        """close the dialog"""
        self.dlg.close() 
        if self.wizard_clicked:
            self.wizard_quickmap_trigger('webservice')
        if self.wizard1_clicked:
            self.wizard_impact_trigger('webservice')    

    #basemap
    def addLayer(self, layerType):
        if layerType.hasGdalTMS():
            # create GDAL TMS layer
            layer = self.createGdalTmsLayer(layerType, layerType.displayName)
        else:
            # create OpenlayersLayer
            layer = OpenlayersLayer(self.iface, self._olLayerTypeRegistry)
            layer.setLayerName(layerType.displayName)
            layer.setLayerType(layerType)

        if layer.isValid():
            coordRefSys = layerType.coordRefSys(self.canvasCrs())
            self.setMapCrs(coordRefSys)
            QgsMapLayerRegistry.instance().addMapLayer(layer)

            # last added layer is new reference
            self.setReferenceLayer(layer)

            if not layerType.hasGdalTMS():
                msg = "Printing and rotating of Javascript API " \
                      "based layers is currently not supported!"
                self.iface.messageBar().pushMessage(
                    "OpenLayers Plugin", msg, level=QgsMessageBar.WARNING,
                    duration=5)

    def setReferenceLayer(self, layer):
        self.layer = layer

    def removeLayer(self, layerId):
        if self.layer is not None:
            if QGis.QGIS_VERSION_INT >= 10900:
                if self.layer.id() == layerId:
                    self.layer = None
            else:
                if self.layer.getLayerID() == layerId:
                    self.layer = None
            # TODO: switch to next available OpenLayers layer?

    def canvasCrs(self):
        mapCanvas = self.iface.mapCanvas()
        if QGis.QGIS_VERSION_INT >= 20300:
            #crs = mapCanvas.mapRenderer().destinationCrs()
            crs = mapCanvas.mapSettings().destinationCrs()
        elif QGis.QGIS_VERSION_INT >= 10900:
            crs = mapCanvas.mapRenderer().destinationCrs()
        else:
            crs = mapCanvas.mapRenderer().destinationSrs()
        return crs

    def setMapCrs(self, coordRefSys):
        mapCanvas = self.iface.mapCanvas()
        # On the fly
        if QGis.QGIS_VERSION_INT >= 20300:
            mapCanvas.setCrsTransformEnabled(True)
        else:
            mapCanvas.mapRenderer().setProjectionsEnabled(True)
        canvasCrs = self.canvasCrs()
        if canvasCrs != coordRefSys:
            coordTrans = QgsCoordinateTransform(canvasCrs, coordRefSys)
            extMap = mapCanvas.extent()
            extMap = coordTrans.transform(extMap, QgsCoordinateTransform.ForwardTransform)
            if QGis.QGIS_VERSION_INT >= 20300:
                mapCanvas.setDestinationCrs(coordRefSys)
            elif QGis.QGIS_VERSION_INT >= 10900:
                mapCanvas.mapRenderer().setDestinationCrs(coordRefSys)
            else:
                mapCanvas.mapRenderer().setDestinationSrs(coordRefSys)
            mapCanvas.freeze(False)
            mapCanvas.setMapUnits(coordRefSys.mapUnits())
            mapCanvas.setExtent(extMap)

    def projectLoaded(self):
        # replace old OpenlayersLayer with GDAL TMS (OL plugin <= 1.3.6)
        rootGroup = self.iface.layerTreeView().layerTreeModel().rootGroup()
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.PluginLayer and layer.pluginLayerType() == OpenlayersLayer.LAYER_TYPE:
                if layer.layerType.hasGdalTMS():
                    # replace layer
                    gdalTMSLayer = self.createGdalTmsLayer(layer.layerType, layer.name())
                    if gdalTMSLayer.isValid():
                        self.replaceLayer(rootGroup, layer, gdalTMSLayer)

    def createGdalTmsLayer(self, layerType, name):
        # create GDAL TMS layer with XML string as datasource
        layer = QgsRasterLayer(layerType.gdalTMSConfig(), name)
        layer.setCustomProperty('ol_layer_type', layerType.layerTypeName)
        return layer

    def replaceLayer(self, group, oldLayer, newLayer):
        index = 0
        for child in group.children():
            if QgsLayerTree.isLayer(child):
                if child.layerId() == oldLayer.id():
                    # insert new layer
                    QgsMapLayerRegistry.instance().addMapLayer(newLayer, False)
                    newLayerNode = group.insertLayer(index, newLayer)
                    newLayerNode.setVisible(child.isVisible())

                    # remove old layer
                    QgsMapLayerRegistry.instance().removeMapLayer(oldLayer.id())

                    msg = "Updated layer '%s' from old OpenLayers Plugin version" % newLayer.name()
                    self.iface.messageBar().pushMessage("OpenLayers Plugin", msg, level=QgsMessageBar.INFO)
                    QgsMessageLog.logMessage(msg, "OpenLayers Plugin", QgsMessageLog.INFO)

                    # layer replaced
                    return True
            else:
                if self.replaceLayer(child, oldLayer, newLayer):
                    # layer replaced in child group
                    return True

            index += 1

        # layer not in this group
        return False

    def setGDALProxy(self):
        proxy = getProxy()

        httpProxyTypes = [QNetworkProxy.DefaultProxy, QNetworkProxy.Socks5Proxy, QNetworkProxy.HttpProxy]
        if QT_VERSION >= 0X040400:
            httpProxyTypes.append(QNetworkProxy.HttpCachingProxy)

        if proxy is not None and proxy.type() in httpProxyTypes:
            # set HTTP proxy for GDAL
            gdalHttpProxy = proxy.hostName()
            port = proxy.port()
            if port != 0:
                gdalHttpProxy += ":%i" % port
            os.environ["GDAL_HTTP_PROXY"] = gdalHttpProxy

            if proxy.user():
                gdalHttpProxyuserpwd = "%s:%s" % (proxy.user(), proxy.password())
                os.environ["GDAL_HTTP_PROXYUSERPWD"] = gdalHttpProxyuserpwd
        else:
            # disable proxy
            os.environ["GDAL_HTTP_PROXY"] = ''
            os.environ["GDAL_HTTP_PROXYUSERPWD"] = ''

    def showGoogleMapsApiKeyDialog(self):
        apiKey = QSettings().value("Plugin-OpenLayers/googleMapsApiKey")
        newApiKey, ok = QInputDialog.getText(self.iface.mainWindow(), "Google Maps API key", "Enter your Google Maps API key", QLineEdit.Normal, apiKey)
        if ok:
            QSettings().setValue("Plugin-OpenLayers/googleMapsApiKey", newApiKey) 

    def run_print(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.print_dlg.show()

        self.print_dlg.title_lineedit.setText('Your Title')
        self.print_dlg.note_lineedit.setText('Put description in here')
        self.print_dlg.disclaimer_lineedit.setText('Put disclaimer')
        self.print_clicked = True
        self.dir_clicked = True
        self.export_to_pdf_clicked = False
        self.export_to_jpg_clicked = False

    def select_dir_map(self):
        filepath = QFileDialog.getExistingDirectory()
        self.print_dlg.output_directory.setText(filepath) 

    def close_print(self):    
        self.print_dlg.close()

    def export_to_pdf(self):
        self.export_to_pdf_clicked = True
        self.make_pdf()

    def to_map_composer(self):
        self.export_to_pdf_clicked = False   
        self.make_pdf() 

    def export_to_jpg(self):
        self.export_to_jpg_clicked = True 
        self.make_pdf()        

    def make_pdf(self):
        if self.print_clicked:
            self.print_clicked = False
            canvas = self.iface.mapCanvas()
            layers = canvas.layers()

            myFile = resources_path('map_layout','layout_qgis_A4.qpt')

            if self.print_dlg.high_res_rb.isChecked():
                myFile = resources_path('map_layout','layout_qgis_A4_300dpi.qpt')
            elif self.print_dlg.mid_res_rb.isChecked():
                myFile = resources_path('map_layout','layout_qgis_A4_200dpi.qpt')
            elif self.print_dlg.low_res_rb.isChecked():
                myFile = resources_path('map_layout','layout_qgis_A4_100dpi.qpt')     

            myTemplateFile = file(myFile, 'rt')
            myTemplateContent = myTemplateFile.read()
            myTemplateFile.close()
            myDocument = QDomDocument()
            myDocument.setContent(myTemplateContent, False)
            comp = self.iface.createNewComposer()
            comp.composition().loadFromTemplate(myDocument)

            map_item = comp.composition().getComposerItemById('map')
            map_item.setMapCanvas(canvas)
            map_item.zoomToExtent(canvas.extent())
            
            legend_item = comp.composition().getComposerItemById('legend')
            legend_item.updateLegend()

            title_item = comp.composition().getComposerItemById('title')
            title_item.setText(self.print_dlg.title_lineedit.text())

            date_time_item = comp.composition().getComposerItemById('date_time')
            date_time_item.setText(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

            note_item = comp.composition().getComposerItemById('note')
            note_item.setText(self.print_dlg.note_lineedit.text())

            disclaimer_item = comp.composition().getComposerItemById('disclaimer')
            disclaimer_item.setText(self.print_dlg.disclaimer_lineedit.text())

            self.get_total_analysis()
            analysis_content_item = comp.composition().getComposerItemById('analysis_content')
            analysis_content_item.setText(self.analysis_content)

            result_lbl_item = comp.composition().getComposerItemById('result_lbl')
            result_lbl_item.setText(self.result_lbl)

            logo_path = resources_path('img','logo.png')
            savap_logo = comp.composition().getComposerItemById('organisation-logo')
            if qgis_version() < 20600:
                savap_logo.setPictureFile(logo_path)
            else:
                savap_logo.setPicturePath(logo_path)

            north_arrow_path = resources_path('img','north_arrows','north_arrow.png')
            north_arrow_item = comp.composition().getComposerItemById('north_wind_pict')
            if qgis_version() < 20600:
                north_arrow_item.setPictureFile(north_arrow_path)
            else:
                north_arrow_item.setPicturePath(north_arrow_path)    
                
            comp.composition().refreshItems()

            file_name = self.print_dlg.filename_prefix.text()
            if file_name == "":
                file_name = "mapreport"

            file_path = self.print_dlg.output_directory.text()
            full_path = ""
                 
            if self.export_to_pdf_clicked:    
                if os.path.isdir(file_path):
                    full_path = file_path+'/'+file_name+'.pdf'
                else:
                    full_path = file_name+'.pdf'
                comp.composition().exportAsPDF(full_path)  
                comp.composerWindow().close()
                QMessageBox.information(None, "Success:", str("Create PDF Success, the file can be found in this directory "+full_path))
            elif self.export_to_jpg_clicked:
                if os.path.isdir(file_path):
                    full_path = file_path+'/'+file_name+'.jpg'
                else:
                    full_path = file_name+'.jpg'
                image = comp.composition().printPageAsRaster(0)    
                image.save(full_path, "jpg") 
                comp.composerWindow().close()
                QMessageBox.information(None, "Success:", str("Create JPG Success, the file can be found in this directory "+full_path))   

            self.close_print()
            if self.wizard_clicked:
                self.wizard_quickmap_trigger()
            if self.wizard1_clicked:
                self.wizard_impact_trigger() 

    def get_total_analysis(self):
        self.analysis_content = ""
        layers = self.iface.legendInterface().layers()
        for data in self.total_geobingan_data:
            print data
            for layer in layers:
                if data == layer.name():
                    self.analysis_content = self.analysis_content + data + " " + str(self.total_geobingan_data[data]) + '<br>'

        for layer in layers:
            if layer.name() == 'Affected Building':
                self.analysis_content = self.analysis_content + self.total_affected_building + '<br>'
            elif layer.name() == 'Affected Population':
                self.analysis_content = self.analysis_content + "Total affected population " + self.total_affected_population + '<br>'
            elif layer.name() == 'Affected Building (grad)':
                self.analysis_content = self.analysis_content + "Total affected building " + self.total_affected_building_grad + '<br>'

        if self.analysis_content != '':
            self.result_lbl = "Result"
        else:
            self.result_lbl = ""             


    def run_opendata(self):
        self.open_data_dlg.show()
        
    def od_geobingan_click(self):
        self.close_open_data()
        self.run_geobingan()   

    def od_osm_downloader_click(self):
        self.close_open_data()
        self.show_osm_downloader()            

    def close_open_data(self):
        self.open_data_dlg.close()
        if self.wizard_clicked:
            self.wizard_quickmap_trigger() 
        if self.wizard1_clicked:
            self.wizard_impact_trigger()     

    def run_geobingan(self):
        self.geobingan_dlg.show()
        
    def geobingan_download_click(self):
        self.progress_dialog = QProgressDialog()
        self.progress_dialog.setAutoClose(False)
        title = self.tr('geoBingAn Downloader')
        self.progress_dialog.setWindowTitle(title)

        self.setMapCrs(self.coordRefSys(4326))
        canvas = self.iface.mapCanvas()
        bbox_str =  str(canvas.extent().yMinimum())+  "," +str(canvas.extent().xMinimum())+ ","+str(canvas.extent().yMaximum()) +","+str(canvas.extent().xMaximum())  
        print bbox_str
        self.download_geobingan_data(bbox_str,self.progress_dialog)
        self.convert_json_vectorpoint()
        self.close_geobingan()
        if self.wizard_clicked:
            self.wizard_quickmap_trigger()
        if self.wizard1_clicked:
            self.wizard_impact_trigger()      

    def download_geobingan_data(self,bbox_str,progress_dialog):
        url = "https://geobingan.info/api/1.2/reports/?bbox="+bbox_str+"&logic=and&num=5000"
       
        if progress_dialog:
            progress_dialog.show()

            # Infinite progress bar when the server is fetching data.
            # The progress bar will be updated with the file size later.
            progress_dialog.setMaximum(0)
            progress_dialog.setMinimum(0)
            progress_dialog.setValue(0)

            # Get a pretty label from feature_type, but not translatable
            label_feature_type = "geoBingAn data"

            label_text = self.tr('Fetching %s' % label_feature_type)
            progress_dialog.setLabelText(label_text)

        # Download Process
        output_path = resources_path('webservice', 'geobingan_data.json')
        downloader = FileDownloader(url, output_path, progress_dialog)
        try:
            result = downloader.download()
        except IOError as ex:
            raise IOError(ex)

        if result[0] is not True:
            _, error_message = result

            if result[0] == QNetworkReply.OperationCanceledError:
                #raise CanceledImportDialogError(error_message)
                pass
            else:
                #raise DownloadError(error_message)  
                pass

        if progress_dialog:
            progress_dialog.close()         

    def convert_json_vectorpoint(self):
        json_data = open(resources_path('webservice', 'geobingan_data.json'))
        data = json.load(json_data)
        json_data.close()
        total_data = len(data)
        total_features = 0
        if total_data > 0:
            geobingan_categories_list = []
            for i in range(0,(total_data - 1)):
                try:
                    if data[i]["category_name"] == 'Shelter' or data[i]["category_name"] == 'Rescue' or data[i]["category_name"] == 'Power Outage' or data[i]["category_name"] == 'Water' or data[i]["category_name"] == 'Fire/Other Incident' or data[i]["category_name"] == 'Damage' or data[i]["category_name"] == 'Flood' or data[i]["category_name"] == 'Landslide':
                        if geobingan_categories_list.index(data[i]["category_name"]) < 0:
                            geobingan_categories_list.append(data[i]["category_name"])
                except Exception as e:
                    geobingan_categories_list.append(data[i]["category_name"])            

            j = 0        
            for category in geobingan_categories_list:
                # Specify the geometry type
                vl = QgsVectorLayer('Point?crs=epsg:4326', category , 'memory')
                vl.startEditing()
                vl.addAttribute(QgsField("category_name", QVariant.String))
                vl.addAttribute(QgsField("content", QVariant.String))
                vl.addAttribute(QgsField("created_time", QVariant.String))
                vl.addAttribute(QgsField("updated_time", QVariant.String))
                vl.addAttribute(QgsField("address", QVariant.String))
                fet = QgsFeature()
                fields = vl.pendingFields()
                fet.setFields( fields, True )
                
                feature_count = 0
                for i in range(0,(total_data - 1)):
                    if category == data[i]["category_name"]:
                        fet.setGeometry( QgsGeometry.fromPoint(QgsPoint(data[i]["lnge6"],data[i]["late6"])) )
                        
                        fet["category_name"] = data[i]["category_name"]
                        fet["content"] = data[i]["content"]
                        fet["created_time"] = data[i]["created_time"]
                        fet["updated_time"] = data[i]["updated_time"]
                        fet["address"] = data[i]["address"]
                        vl.addFeatures( [ fet ] )
                        feature_count += 1    
                        total_features += 1    
                vl.commitChanges()   
                QgsMapLayerRegistry.instance().addMapLayers([vl])
                vl.removeSelection()
                symbols = vl.rendererV2().symbols()
                symbol = symbols[0]
                symbol.setColor(QColor.fromRgb(randint((255/len(geobingan_categories_list)*j),(255/len(geobingan_categories_list)*(j+1))),randint(0,255),randint(0,255)))
                qgis.utils.iface.mapCanvas().refresh() 
                qgis.utils.iface.legendInterface().refreshLayerSymbology(vl) 
                self.total_geobingan_data[category] =  feature_count
                j += 1

        if total_features > 0:        
            QMessageBox.information(None, "Success:", str("Success download data for this area"))   
        else:
            QMessageBox.information(None, "Failed:", str("No data available for this area"))   
        
    def close_geobingan(self):
        self.geobingan_dlg.close()  
            
    #wizard part
    def init_wizard(self):
        self.wizard_clicked = False
        self.wizard1_clicked = False
        self.select_exposure_data_dlg = SelectExposureData()
        self.wizard_quickmap0_dlg = WizardQuickmap0()
        self.wizard_quickmap1_dlg = WizardQuickmap1()
        self.wizard_quickmap2_dlg = WizardQuickmap2()
        self.wizard_impact0_dlg = WizardImpact0()
        self.wizard_impact1_dlg = WizardImpact1()
        self.wizard_impact2_dlg = WizardImpact2()

        self.building_osm_dlg = BuildingOsm()
        self.road_osm_dlg = RoadOsm()
        self.country_detail_adm_dlg = CountryDetailAdm()

        self.country_list = [["am","Armenia","ARM","N"],
        ["au","Australia","AUS","N"],
        ["az","Azerbaijan","AZE","N"],
        ["bd","Bangladesh","BGD","N"],
        ["bt","Bhutan","BTN","N"],
        ["bn","Brunei","BRN","N"],
        ["kh","Cambodia","KHM","N"],
        ["cn","China","CHN","N"],
        ["fj","Fiji","FJI","N"],
        ["in","India","IND","N"],
        ["id","Indonesia","IDN","N"],
        ["ir","Iran","IRN","N"],
        ["jp","Japan","JPN","N"],
        ["kz","Kazakhstan","KAZ","N"],
        ["kr","Korea","KOR","N"],
        ["kg","Kyrgyzstan","KGZ","N"],
        ["la","Lao PDR","LAO","N"],
        ["my","Malaysia","MYS","N"],
        ["mv","Maldives","MDV","N"],
        ["mn","Mongolia","MNG","N"],
        ["mm","Myanmar","MMR","N"],
        ["np","Nepal","NPL","N"],
        ["pk","Pakistan","PAK","N"],
        ["pg","Papua New Guinea","PNG","N"],
        ["ph","Philippines","PHL","N"],
        ["ru","Russia","RUS","N"],
        ["sg","Singapore","SGP","N"],
        ["lk","Sri Lanka","LKA","N"],
        ["tw","Taiwan","TWN","N"],
        ["tj","Tajikistan","TJK","N"],
        ["th","Thailand","THA","N"],
        ["uz","Uzbekistan","UZB","N"],
        ["vn","Vietnam","VNM","N"],
        ["ye","Yemen","YEM","N"]]

        if os.path.exists(resources_path('webservice', 'countries.json')) == False:
            self.create_file_countries_download()
        else:
            self.read_file_countries()    

        country_cb_list = []
        for country in self.country_list:
            country_cb_list.append(country[1])
        #country_list.append("All")

        disaster_list = []
        disaster_list.append("All")
        disaster_list.append("Flood")
        disaster_list.append("Earthquake")
        disaster_list.append("Landslide")

        analysis_list = []
        analysis_list.append("Affected Building")
        analysis_list.append("Affected Building (grad)")
        analysis_list.append("Affected Population")

        self.wizard_quickmap0_dlg.country_comboBox.clear()
        self.wizard_quickmap0_dlg.country_comboBox.addItems(country_cb_list)

        self.wizard_quickmap0_dlg.disaster_type_comboBox.clear()
        self.wizard_quickmap0_dlg.disaster_type_comboBox.addItems(disaster_list)

        self.wizard_impact0_dlg.country_comboBox.clear()
        self.wizard_impact0_dlg.country_comboBox.addItems(country_cb_list)

        self.wizard_impact0_dlg.disaster_type_comboBox.clear()
        self.wizard_impact0_dlg.disaster_type_comboBox.addItems(disaster_list)

        self.wizard_impact0_dlg.analysis_comboBox.clear()
        self.wizard_impact0_dlg.analysis_comboBox.addItems(analysis_list)

        self.road_osm_dlg.browse_file_btn.setDisabled(True)
        self.building_osm_dlg.browse_file_btn.setDisabled(True)

    def filter_data_quickmap(self):
        country_cb = str(self.wizard_quickmap0_dlg.country_comboBox.currentText()).lower()
        disaster_cb = str(self.wizard_quickmap0_dlg.disaster_type_comboBox.currentText()).lower()
        foundDatasets = []
        for dataset in self.datasets:
            country = dataset.country.lower()
            disasterType = dataset.typeDisaster.lower()
            
            if country_cb == "all" and disaster_cb != "all":
                if disaster_cb in disasterType: 
                    foundDatasets.append(dataset)
            elif country_cb == "all" and disaster_cb == "all":  
                foundDatasets.append(dataset)
            elif country_cb != "all" and disaster_cb == "all":
                if country_cb in country: 
                    foundDatasets.append(dataset)  
            elif country_cb != "all" and disaster_cb != "all":          
                if (country_cb in country and disaster_cb == "") or (country_cb in country and disaster_cb in disasterType):            
                    foundDatasets.append(dataset)
        #fill the table with the found datasets
        self.datasets = foundDatasets
        self.fill_table(foundDatasets)

    def filter_data_impactmap(self, map_type):
        country_cb = str(self.wizard_impact0_dlg.country_comboBox.currentText()).lower()
        disaster_cb = str(self.wizard_impact0_dlg.disaster_type_comboBox.currentText()).lower()
        foundDatasets = []
        for dataset in self.datasets:
            country = dataset.country.lower()
            disasterType = dataset.typeDisaster.lower()
            mapFormat = dataset.mapFormat.lower()
            mapType_ = dataset.mapType
            
            if mapFormat == "raster" or mapFormat == "vector":  
                if country_cb in country and mapType_ == map_type: 
                    foundDatasets.append(dataset)  
               
        #fill the table with the found datasets
        self.datasets = foundDatasets
        self.fill_table(foundDatasets)          

    def run_wizard(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.wizard_clicked = True
        self.run_basemap()

    def basemap_default(self):
        layers = self.iface.legendInterface().layers()
        osm_layer_available = False
        for layer in layers:
            # create an item with a caption
            if layer.name() == 'World':
                osm_layer_available = True

        if osm_layer_available == False:
            self.countries_downloader()
            self.setMapCrs(self.coordRefSys(4326))
            path_layer = resources_path('countries_admin','ne_10m_admin_0_countries', 'ne_10m_admin_0_countries')
            layer = self.iface.addVectorLayer(path_layer+'.shp', 'World', "ogr")
            canvas = self.iface.mapCanvas()
            extent = layer.extent()
            canvas.setExtent(extent)
            canvas.refresh()

            palyr = QgsPalLayerSettings()
            palyr.readFromLayer(layer)
            palyr.enabled = True
            palyr.fieldName = 'NAME'
            palyr.placement= QgsPalLayerSettings.OverPoint
            palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
            palyr.writeToLayer(layer)

    def country_extend(self, idx):
        country = self.country_list[idx]
        country_json_data = open(resources_path('minimum_needs', country[0]+'.json'))
        data = json.load(country_json_data)
        country_json_data.close()
        extent = data["bbox"]
        wkt = 'POINT(%s %s)' % (extent[0][0],extent[0][1])
        geom = QgsGeometry.fromWkt(wkt)
        if len(extent)>1:
            newExtent = QgsRectangle(extent[0][0],extent[0][1],extent[1][2],extent[1][3]) 
        else:
            newExtent = QgsRectangle(geom.centroid().asPoint())
            newExtent.scale(1, geom.centroid().asPoint())
        
        #self.setMapCrs(self.coordRefSys(4326))
        canvas = self.iface.mapCanvas()
        canvas.setExtent(newExtent)
        canvas.refresh()   
        canvas.zoomScale(4000)
        extent = viewport_geo_array(self.iface.mapCanvas())
        self.update_extent_ls(extent)

    def country_extend1(self, country):
        canvas = self.iface.mapCanvas()
        layer = QgsMapLayerRegistry.instance().mapLayersByName('World')[0]
        layer.removeSelection()
        expr = QgsExpression("\"NAME\"='"+country+"'")
        it = layer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        layer.setSelectedFeatures(ids)
        canvas.zoomToSelected(layer)
        canvas.refresh()

    def run_wizard_quickmap0(self):
        if self.wizard_clicked == False:
            self.wizard_clicked = True
            self.basemap_default()

            self.wizard_quickmap0_dlg.show()
            self.update_wizard_layers_listView()
            self.country_extend1(self.wizard_quickmap0_dlg.country_comboBox.currentText())
            #self.country_extend(self.wizard_impact0_dlg.country_comboBox.currentIndex())
        
    def run_wizard_quickmap1(self):
        self.wizard_quickmap0_dlg.close()
        self.wizard_quickmap1_dlg.show()
            
    def run_wizard_quickmap2(self):
        self.wizard_quickmap1_dlg.close()
        self.wizard_quickmap2_dlg.show()
        
    def back_wizard_quickmap1(self):
        self.wizard_quickmap1_dlg.close()   
        self.wizard_quickmap0_dlg.show()

    def back_wizard_quickmap2(self):
        self.wizard_quickmap2_dlg.close()   
        self.wizard_quickmap1_dlg.show()  

    def close_wizard_quickmap0(self):
        self.wizard_quickmap0_dlg.close() 
        self.wizard_clicked = False    

    def close_wizard_quickmap2(self):
        self.wizard_quickmap2_dlg.close() 
        self.wizard_clicked = False

    def wiz_delete_layers_btn_click(self):
        layers = self.iface.legendInterface().layers()
        layer_list = []
        i = 0
        for layer in layers:
            if self.model.item(i).checkState() == 2:
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
            i += 1 
        self.update_wizard_layers_listView()

    def wiz_delete1_layers_btn_click(self):
        layers = self.iface.legendInterface().layers()
        layer_list = []
        i = 0
        for layer in layers:
            if self.model1.item(i).checkState() == 2:
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
            i += 1 
        self.update_wizard_layers_listView()               
        
    def update_wizard_layers_listView(self):
        list = self.wizard_quickmap1_dlg.layers_listView
        list1 = self.wizard_quickmap2_dlg.layers_listView
         
        # Create an empty model for the list's data
        self.model = QStandardItemModel(list)
        self.model1 = QStandardItemModel(list1)
         
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            # create an item with a caption
            item = QStandardItem(layer.name())
            # add a checkbox to it
            item.setCheckable(True)
            # Add the item to the model
            self.model.appendRow(item)

            # create an item with a caption
            item1 = QStandardItem(layer.name())
            # add a checkbox to it
            item1.setCheckable(True)
            # Add the item to the model
            self.model1.appendRow(item1)
        
        #self.model.itemChanged.connect(self.on_wizard_layers_listView_item_changed)

        # Apply the model to the list view
        list.setModel(self.model)
        list1.setModel(self.model1)         
         
    def wizard_quickmap_trigger(self,method_name=''):
        self.update_wizard_layers_listView()  
        if method_name == 'webservice':
            self.datasets = self.datasets_temp
            self.fill_table(self.datasets)

    def run_wizard_impact0(self):
        #self.country_downloader('Bangladesh','BGD')
        if self.wizard1_clicked == False:
            self.wizard1_clicked = True
            self.impact_layer_list = []
            self.basemap_default()
            self.country_extend1(self.wizard_impact0_dlg.country_comboBox.currentText())
            self.wizard_impact0_dlg.show()
            self.update_wizard1_layers_listView()
            

    def check_impact_layer(self,type_data,layer_name):
        data_exist = False
        for layer in self.impact_layer_list:
            if type_data == layer[0]:
                layer[1] = layer_name
                data_exist = True

        if data_exist == False:
            self.impact_layer_list.append([type_data,layer_name])
        if len(self.impact_layer_list)>=2:
            self.wizard_impact1_dlg.run_analysis_btn.setDisabled(False)


    def close_wizard_impact0(self):
        self.wizard_impact0_dlg.close() 
        self.wizard1_clicked = False    
        
    def run_wizard_impact1(self):
        self.wizard_impact0_dlg.close()
        self.wizard_impact1_dlg.show()
        if self.wizard_impact0_dlg.analysis_comboBox.currentText() == "Affected Building" or self.wizard_impact0_dlg.analysis_comboBox.currentText() == "Affected Building (grad)":
            self.wizard_impact1_dlg.label_data_analysis.setText("Select building data")
        else:    
            self.wizard_impact1_dlg.label_data_analysis.setText("Select population data")

        if len(self.impact_layer_list)>=2:
            self.wizard_impact1_dlg.run_analysis_btn.setDisabled(False)    
        else:
            self.wizard_impact1_dlg.run_analysis_btn.setDisabled(True)
            
    def run_wizard_impact2(self):
        self.wizard_impact1_dlg.close()
        self.wizard_impact2_dlg.show()
            
    def back_wizard_impact1(self):
        self.wizard_impact1_dlg.close()   
        self.wizard_impact0_dlg.show()

    def back_wizard_impact2(self):
        self.wizard_impact2_dlg.close()   
        self.wizard_impact1_dlg.show()  

    def close_wizard_impact2(self):
        self.wizard_impact2_dlg.close() 
        self.wizard1_clicked = False

    def run_country_detail_adm(self):
        self.load_data_country_adm()
        self.country_detail_adm_dlg.show()

    def country_adm_download_button_click(self):
        idCountry = self.wizard_impact0_dlg.country_comboBox.currentIndex()
        self.country_downloader(self.country_list[idCountry][1],self.country_list[idCountry][2])        
        self.load_data_country_adm()

    def load_data_country_adm(self):
        idCountry = self.wizard_impact0_dlg.country_comboBox.currentIndex()
        country = self.country_list[idCountry][1]
        self.country_detail_adm_dlg.download_label.setText('Administrative boundaries for '+country)
        if os.path.exists(resources_path('countries_admin', self.country_list[idCountry][2],self.country_list[idCountry][2]+'_adm0.shp')) == False:
            self.country_detail_adm_dlg.download_button.show()
        else:
            self.country_detail_adm_dlg.download_button.hide()
            
            #adm1
            path_file = resources_path('countries_admin',self.country_list[idCountry][2],self.country_list[idCountry][2]+'_adm1.shp')
            layer = QgsVectorLayer(path_file, country, 'ogr')
            list_adm1 = []
            for feature in layer.getFeatures():
                list_adm1.append( feature['NAME_1'] )

            self.country_detail_adm_dlg.adm1_comboBox.clear()
            self.country_detail_adm_dlg.adm1_comboBox.addItems(list_adm1)

            #adm2
            path_file = resources_path('countries_admin',self.country_list[idCountry][2],self.country_list[idCountry][2]+'_adm2.shp')
            if os.path.exists(path_file):
                self.country_detail_adm_dlg.adm2_comboBox.setDisabled(False)
                self.country_detail_adm_dlg.adm2_radio.setDisabled(False)
                layer = QgsVectorLayer(path_file, country, 'ogr')
                list_adm2 = []
                for feature in layer.getFeatures():
                    list_adm2.append( feature['NAME_2'] )

                self.country_detail_adm_dlg.adm2_comboBox.clear()
                self.country_detail_adm_dlg.adm2_comboBox.addItems(list_adm2)
            else:
                self.country_detail_adm_dlg.adm2_comboBox.setDisabled(True)
                self.country_detail_adm_dlg.adm2_radio.setDisabled(True)

            #adm3
            path_file = resources_path('countries_admin',self.country_list[idCountry][2],self.country_list[idCountry][2]+'_adm3.shp')
            if os.path.exists(path_file):
                self.country_detail_adm_dlg.adm3_comboBox.setDisabled(False)
                self.country_detail_adm_dlg.adm3_radio.setDisabled(False)
                layer = QgsVectorLayer(path_file, country, 'ogr')
                list_adm3 = []
                for feature in layer.getFeatures():
                    list_adm3.append( feature['NAME_3'] )

                self.country_detail_adm_dlg.adm3_comboBox.clear()
                self.country_detail_adm_dlg.adm3_comboBox.addItems(list_adm3)
            else:
                self.country_detail_adm_dlg.adm3_comboBox.setDisabled(True)
                self.country_detail_adm_dlg.adm3_radio.setDisabled(True)

    def country_adm_extend(self, adm_name,layer,field_name):
        canvas = self.iface.mapCanvas()
        layer.removeSelection()
        expr = QgsExpression("\""+field_name+"\"='"+adm_name+"'")
        it = layer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        layer.setSelectedFeatures(ids)
        canvas.zoomToSelected(layer)
        canvas.refresh()            

    def load_country_adm(self):
        idCountry = self.wizard_impact0_dlg.country_comboBox.currentIndex()
        country = self.country_list[idCountry][1]
        if self.country_detail_adm_dlg.adm1_radio.isChecked():
            adm = self.country_detail_adm_dlg.adm1_comboBox.currentText()
            path_file = resources_path('countries_admin',self.country_list[idCountry][2],self.country_list[idCountry][2]+'_adm1.shp')
            layer = QgsVectorLayer(path_file, country + " province", 'ogr')
            QgsMapLayerRegistry.instance().addMapLayers( [layer] )
            palyr = QgsPalLayerSettings()
            palyr.readFromLayer(layer)
            palyr.enabled = True
            palyr.fieldName = 'NAME_1'
            palyr.placement= QgsPalLayerSettings.OverPoint
            palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
            palyr.writeToLayer(layer)
            self.country_adm_extend(adm,layer,'NAME_1')
        elif self.country_detail_adm_dlg.adm2_radio.isChecked():
            adm = self.country_detail_adm_dlg.adm2_comboBox.currentText()
            path_file = resources_path('countries_admin',self.country_list[idCountry][2],self.country_list[idCountry][2]+'_adm2.shp')
            layer = QgsVectorLayer(path_file, country + " district", 'ogr')
            QgsMapLayerRegistry.instance().addMapLayers( [layer] )
            palyr = QgsPalLayerSettings()
            palyr.readFromLayer(layer)
            palyr.enabled = True
            palyr.fieldName = 'NAME_2'
            palyr.placement= QgsPalLayerSettings.OverPoint
            palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
            palyr.writeToLayer(layer)
            self.country_adm_extend(adm,layer,'NAME_2')
        elif self.country_detail_adm_dlg.adm3_radio.isChecked():
            adm = self.country_detail_adm_dlg.adm3_comboBox.currentText()
            path_file = resources_path('countries_admin',self.country_list[idCountry][2],self.country_list[idCountry][2]+'_adm3.shp')
            layer = QgsVectorLayer(path_file, country + " sub-district", 'ogr')
            QgsMapLayerRegistry.instance().addMapLayers( [layer] )
            palyr = QgsPalLayerSettings()
            palyr.readFromLayer(layer)
            palyr.enabled = True
            palyr.fieldName = 'NAME_3'
            palyr.placement= QgsPalLayerSettings.OverPoint
            palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
            palyr.writeToLayer(layer)
            self.country_adm_extend(adm,layer,'NAME_3')
        self.country_detail_adm_dlg.close() 

    def close_country_detail_adm(self):
        self.country_detail_adm_dlg.close()           

    def wiz1_delete_layers_btn_click(self):
        layers = self.iface.legendInterface().layers()
        i = 0
        new_layer = []
        for layer in self.impact_layer_list:
            if self.model_impact.item(i).checkState() == 2:
                QgsMapLayerRegistry.instance().removeMapLayer(QgsMapLayerRegistry.instance().mapLayersByName(layer[1])[0])
            else:
                new_layer.append(layer)
            i += 1 

        self.impact_layer_list = new_layer
        if len(self.impact_layer_list)>=2:
            self.wizard_impact1_dlg.run_analysis_btn.setDisabled(False)    
        else:
            self.wizard_impact1_dlg.run_analysis_btn.setDisabled(True)
        self.update_wizard1_layers_listView()

    def wiz1_delete1_layers_btn_click(self):
        print "call"
        layers = self.iface.legendInterface().layers()
        layer_list = []
        i = 0
        for layer in layers:
            if self.model1_impact.item(i).checkState() == 2:
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
            i += 1 
        self.update_wizard1_layers_listView()               
        
    def update_wizard1_layers_listView(self):
        list = self.wizard_impact1_dlg.layers_listView
        list1 = self.wizard_impact2_dlg.layers_listView
         
        # Create an empty model for the list's data
        self.model_impact = QStandardItemModel(list)
        self.model1_impact = QStandardItemModel(list1)
         
        for layer in self.impact_layer_list:
            # create an item with a caption
            item = QStandardItem(layer[1])
            # add a checkbox to it
            item.setCheckable(True)
            # Add the item to the model
            self.model_impact.appendRow(item)

        layers = self.iface.legendInterface().layers()
        for layer in layers:
            # create an item with a caption
            item1 = QStandardItem(layer.name())
            # add a checkbox to it
            item1.setCheckable(True)
            # Add the item to the model
            self.model1_impact.appendRow(item1)
        
        #self.model.itemChanged.connect(self.on_wizard_layers_listView_item_changed)

        # Apply the model to the list view
        list.setModel(self.model_impact)
        list1.setModel(self.model1_impact)

    def run_wizard_analysis(self):
        if self.wizard_impact0_dlg.analysis_comboBox.currentText() == "Affected Building":
            points = None
            poly = None
            for layer in self.impact_layer_list:
                if layer[0] == "Building":
                    points=QgsMapLayerRegistry.instance().mapLayersByName(layer[1])[0]
                if layer[0] == "VAP":
                    poly=QgsMapLayerRegistry.instance().mapLayersByName(layer[1])[0] 
            if points != None and poly != None:        
                self.points_in_polygon_analysis1(points,poly)
            else:
                QMessageBox.information(None, "ERROR:", str("Layers not correct"))
        elif self.wizard_impact0_dlg.analysis_comboBox.currentText() == "Affected Population": 
            raster = None
            poly = None
            for layer in self.impact_layer_list:
                if layer[0] == "Population":
                    raster=QgsMapLayerRegistry.instance().mapLayersByName(layer[1])[0]
                if layer[0] == "VAP":
                    poly=QgsMapLayerRegistry.instance().mapLayersByName(layer[1])[0] 
            if raster != None and poly != None:        
                self.population_analysis(raster,poly)
            else:
                QMessageBox.information(None, "ERROR:", str("Layers not correct"))
        elif self.wizard_impact0_dlg.analysis_comboBox.currentText() == "Affected Building (grad)":
            points = None
            poly = None
            for layer in self.impact_layer_list:
                if layer[0] == "Building":
                    points=QgsMapLayerRegistry.instance().mapLayersByName(layer[1])[0]
                if layer[0] == "VAP":
                    poly=QgsMapLayerRegistry.instance().mapLayersByName(layer[1])[0] 
            if points != None and poly != None:        
                self.points_in_polygon_analysis2(points,poly)
            else:
                QMessageBox.information(None, "ERROR:", str("Layers not correct"))

        self.update_wizard1_layers_listView()        
        
    def wizard_impact_trigger(self,method_name=''):
        self.update_wizard1_layers_listView() 
        if method_name == 'webservice':
            self.datasets = self.datasets_temp
            self.fill_table(self.datasets)              

    def run_select_exposure_data(self):
        self.select_exposure_data_dlg.show()
        
    def wiz_import_data_click(self):
        self.close_select_exposure_data()
        self.run_importdata()   

    def wiz_osm_downloader_click(self):
        self.close_select_exposure_data()
        self.show_osm_downloader()            

    def close_select_exposure_data(self):
        self.select_exposure_data_dlg.close()   

    def select_analysis_data(self):
        if self.wizard_impact0_dlg.analysis_comboBox.currentText() == "Affected Building" or self.wizard_impact0_dlg.analysis_comboBox.currentText() == "Affected Building (grad)":
            self.show_building_osm()
        else:
            self.run_loadwebservice('impactmap1')          
            
    def execute_analysis(self):
        if self.analysis_dlg.affected_building_radio.isChecked():
            points=QgsMapLayerRegistry.instance().mapLayersByName(self.analysis_dlg.exposure_layer_comboBox.currentText())[0]
            poly=QgsMapLayerRegistry.instance().mapLayersByName(self.analysis_dlg.hazard_layer_comboBox.currentText())[0]
            self.points_in_polygon_analysis1(points,poly)
        elif self.analysis_dlg.affected_population_radio.isChecked():
            raster=QgsMapLayerRegistry.instance().mapLayersByName(self.analysis_dlg.exposure_layer_comboBox.currentText())[0]
            poly=QgsMapLayerRegistry.instance().mapLayersByName(self.analysis_dlg.hazard_layer_comboBox.currentText())[0]
            self.population_analysis(raster,poly)
        elif self.analysis_dlg.affected_building1_radio.isChecked():
            points=QgsMapLayerRegistry.instance().mapLayersByName(self.analysis_dlg.exposure_layer_comboBox.currentText())[0]
            poly=QgsMapLayerRegistry.instance().mapLayersByName(self.analysis_dlg.hazard_layer_comboBox.currentText())[0]
            self.points_in_polygon_analysis2(points,poly)    

        print "finish"  
        self.analysis_dlg.close()
        
        if self.wizard1_clicked:
            self.wizard_impact_trigger()    
        
    def points_in_polygon_analysis1(self,points,poly):
        try:
            path_layer = resources_path('webservice', 'memory1')

            try:
                if os.path.exists(resources_path('webservice', 'memory1.shp')):
                    os.remove(path_layer+'.shp')
                    os.remove(path_layer+'.dbf')
                    os.remove(path_layer+'.prj')
                    os.remove(path_layer+'.qpj')
                    os.remove(path_layer+'.shx')
            except IOError as ex:
                raise IOError(ex)    
            
            #alg_processing = Processing.getAlgorithm("qgis:intersection")
            #alg_processing_len = len(alg_processing.parameters)
            print qgis_version()
            alg = Intersection.Intersection()
            alg.setParameterValue('INPUT', points)
            alg.setParameterValue('INPUT2', poly)
            alg.setParameterValue('IGNORE_NULL', True)
            alg.setOutputValue('OUTPUT', path_layer)
            
            progress = SilentProgress()
            alg.processAlgorithm(progress)
            """
            if qgis_version() >= 21800:
                processing.runalg("qgis:intersection",points,poly,True,path_layer)
            else:
                processing.runalg("qgis:intersection",points,poly,path_layer)
            """
            layer = self.iface.addVectorLayer(path_layer+'.shp', 'Affected Building', "ogr")
            
            try:
                # count total points
                countPointOriginal = 0
                feats_point_original =points.getFeatures()
                for feature in feats_point_original:
                    countPointOriginal += 1
            except IOError as ex:
                raise IOError(ex)

            try:
                # Select the intersected result
                countPoint = 0
                feats_point =layer.getFeatures()
                for feature in feats_point:
                    countPoint += 1
            except IOError as ex:
                raise IOError(ex)
   
            self.total_affected_building = "Total affected building " + str(countPoint) + " of "+ str(countPointOriginal)
            QMessageBox.information(None, "Success:", str("Analysis Success, new layer Affected Building created"))
            print countPoint
        except IOError as ex:
            QMessageBox.information(None, "ERROR:", str("Invalid layers"))
            raise IOError(ex)
                 
        

    def points_in_polygon_analysis2(self,points,poly):
        try:
            path_layer = resources_path('webservice', 'memory3')

            if os.path.exists(resources_path('webservice', 'memory3.shp')):
                os.remove(path_layer+'.shp')
                os.remove(path_layer+'.dbf')
                os.remove(path_layer+'.prj')
                os.remove(path_layer+'.qpj')
                os.remove(path_layer+'.shx')

            alg = PointsInPolygon.PointsInPolygon()
            alg.setParameterValue('POLYGONS', poly)
            alg.setParameterValue('POINTS', points)
            alg.setParameterValue('FIELD', 'NUMPOINTS')
            alg.setOutputValue('OUTPUT', path_layer)
            progress = SilentProgress()
            alg.processAlgorithm(progress)

            #processing.runalg("qgis:countpointsinpolygon",poly,points,'NUMPOINTS',path_layer)
            layer = QgsVectorLayer(path_layer+'.shp', 'Affected Building (grad)', 'ogr')

            targetField = 'NUMPOINTS'
            classes = 5
            if layer.isValid():
                self.applySymbologyEqualTotalValue(layer, classes, targetField)
                self.total_affected_building_grad = self.total_analysis_with_grad
                QgsMapLayerRegistry.instance().addMapLayers( [layer] )   
                QMessageBox.information(None, "Success:", str("Analysis Success, new layer Affected Building (grad) created"))
        except IOError as ex:
            QMessageBox.information(None, "ERROR:", str("Invalid layers"))
            raise IOError(ex)

              

    def population_analysis(self,raster,poly):
        try:
            path_layer = resources_path('webservice', 'memory2')

            if os.path.exists(resources_path('webservice', 'memory2.shp')):
                os.remove(path_layer+'.shp')
                os.remove(path_layer+'.dbf')
                os.remove(path_layer+'.prj')
                os.remove(path_layer+'.qpj')
                os.remove(path_layer+'.shx')

            alg = ZonalStatistics.ZonalStatistics()
            alg.setParameterValue('INPUT_RASTER', raster)
            alg.setParameterValue('RASTER_BAND', 1)
            alg.setParameterValue('INPUT_VECTOR', poly)
            alg.setParameterValue('COLUMN_PREFIX', '_')
            alg.setParameterValue('GLOBAL_EXTENT', False)
            alg.setOutputValue('OUTPUT_LAYER', path_layer)
            progress = SilentProgress()
            alg.processAlgorithm(progress)
            #processing.runalg("qgis:zonalstatistics",raster,1,poly,'_',False,path_layer)
            layer = QgsVectorLayer(path_layer+'.shp', 'Affected Population', 'ogr')

            targetField = '_count'
            classes = 5
            if layer.isValid():
                self.applySymbologyEqualTotalValue(layer, classes, targetField)
                self.total_affected_population = self.total_analysis_with_grad
                QgsMapLayerRegistry.instance().addMapLayers( [layer] )   
                QMessageBox.information(None, "Success:", str("Analysis Success, new layer Affected Population created"))
        except IOError as ex:
            QMessageBox.information(None, "ERROR:", str("Invalid layers"))
            raise IOError(ex)

         

    def getSortedFloatsFromAttributeTable( self, layer, fieldName ):
        values = []
        for feature in layer.getFeatures():
            values.append( feature[fieldName] )

        values.sort()
        return values

    def validatedDefaultSymbol( self, geometryType ):
        symbol = QgsSymbolV2.defaultSymbol( geometryType )
        if symbol is None:
            if geometryType == QGis.Point:
                symbol = QgsMarkerSymbolV2()
            elif geometryType == QGis.Line:
                symbol = QgsLineSymbolV2 ()
            elif geometryType == QGis.Polygon:
                symbol = QgsFillSymbolV2 ()
        return symbol    

    def makeSymbologyForRange( self, layer, min , max, title, color):
        symbol = self.validatedDefaultSymbol( layer.geometryType() )
        symbol.setColor( color )
        range = QgsRendererRangeV2( min, max, symbol, title )
        return range    

    def arbitaryColor( self, amount, max ):
        color = QColor()
        number_color =240 * amount / float( max - 1 )
        color.setHsv( 240 - number_color, 255, 255 )
        return color

    def makeGraduatedRendererFromDivisionsList( self, layer, fieldName, divisions ):
        classes = len( divisions ) - 1
        rangeList = []
        for i in range( classes ):
            label = str( int(divisions[i]) ) + " to " + str( int(divisions[i+1]) )
            rangeList.append( self.makeSymbologyForRange( layer, divisions[i] , divisions[i+1], label, self.arbitaryColor( i, classes ) ) )
        renderer = QgsGraduatedSymbolRendererV2( fieldName, rangeList )
        renderer.setMode( QgsGraduatedSymbolRendererV2.Custom )
        return renderer

    def applySymbologyEqualTotalValue( self, layer, classes, fieldName):
        values = self.getSortedFloatsFromAttributeTable( layer, fieldName )
        total = sum( values )

        self.total_analysis_with_grad = str( int(total))

        step = total / float( classes )
        nextStep = step
        divisions = [ values[0] ]
        runningTotal = 0
        for value in values:
            runningTotal += value
            if runningTotal >= nextStep:
                divisions.append( value )
                nextStep += step
        if divisions[-1] != values[-1]:
            divisions.append(values[-1])
        renderer = self.makeGraduatedRendererFromDivisionsList( layer, fieldName, divisions )
        layer.setRendererV2( renderer ) 

    def change_canvas_proj(self, proj_number):
        canvas = self.iface.mapCanvas()
        wgsCRS = QgsCoordinateReferenceSystem(proj_number)
        canvas.mapRenderer().setProjectionsEnabled(True)
        canvas.mapRenderer().setDestinationCrs(wgsCRS) 

    def coordRefSys(self, epsg_number):
        epsg = epsg_number  # TODO: look for matching coord
        coordRefSys = QgsCoordinateReferenceSystem()
        createCrs = coordRefSys.createFromOgcWmsCrs("EPSG:%d" % epsg)
        if not createCrs:
            return None
        return coordRefSys  

    #search location
    def run_location_search(self):
        self.location_search_dlg.show()
        self.country_extend1(self.wizard_quickmap0_dlg.country_comboBox.currentText())
        #self.country_extend(self.wizard_impact0_dlg.country_comboBox.currentIndex())

    def init_location_search(self):
        self.location_search_dlg = LocationSearch()
        
        #self.rb = QgsRubberBand(self.canvas, QGis.Point)
        #self.rb.setColor(QColor( 255, 0, 0, 150 ))
        self.searchCacheLimit = 1000
        
        self.wgs84 = QgsCoordinateReferenceSystem()
        self.wgs84.createFromSrid(4326)
        self.proj = self.canvas.mapRenderer().destinationCrs()
        self.transform = QgsCoordinateTransform(self.wgs84, self.proj)
        
        self.location_search_dlg.bSearch.clicked.connect(self.startSearch)
        self.location_search_dlg.eOutput.currentItemChanged.connect(self.itemChanged)
        #self.location_search_dlg.eOutput.clickedOutsideOfItems.connect(self.itemChanged)
        #self.location_search_dlg.eText.cleared.connect(self.clearEdit)
        self.canvas.mapRenderer().destinationSrsChanged.connect(self.crsChanged)
        
        db = cacheDB()
        self.autocompleteList = db.getAutocompleteList()
        db.closeConnection()
        self.completer = QCompleter(self.autocompleteList)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.location_search_dlg.eText.setCompleter(self.completer)

        self.setTableLSWidgetBehavour()

        self.rectangle_map_tool = \
            RectangleMapTool(self.canvas)
        self.rectangle_map_tool.rectangle_created.connect(
            self.update_extent_from_rectangle)

        # Setup pan tool
        self.pan_tool = QgsMapToolPan(self.canvas)
        self.canvas.setMapTool(self.pan_tool)

    def setTableLSWidgetBehavour(self):
        self.location_search_dlg.eOutput.setColumnWidth(0,400)
        self.location_search_dlg.eOutput.setColumnWidth(1,100)
        self.location_search_dlg.eOutput.setColumnWidth(2,0)
        self.location_search_dlg.eOutput.setColumnHidden(2,True)
        self.location_search_dlg.eOutput.header().setResizeMode(0, QHeaderView.Stretch)
        self.location_search_dlg.eOutput.header().setStretchLastSection(False)

    def startSearch(self):
        country_cb = str(self.wizard_quickmap0_dlg.country_comboBox.currentText()).lower()
        text = self.location_search_dlg.eText.text().encode('utf-8')
        if text == "":
            self.clearEdit()

        if country_cb == "all":
            country_cb = ""
        else:
            country_cb = country_cb +', '
        #url = 'http://open.mapquestapi.com/nominatim/v1/search.php'
        url = 'http://nominatim.openstreetmap.org/search'
        self.location_search_dlg.search_result_lbl.setText('Searching...')
        params = urllib.urlencode({'q': country_cb + text,'format': 'json','polygon_text':'1'})
        #print url+'?'+params
        response = json.load(urllib2.urlopen(url+'?'+params))
        self.loadData(response)
        self.setTableLSWidgetBehavour()

    def loadData(self, data):
        #self.rb.reset(QGis.Point)
        self.location_search_dlg.eOutput.clear()
        items = []
        #print data
        for d in data:
            try:
                geometry = d['geotext']
            except KeyError:
                geometry = 'POINT(%s %s)' % (d['lon'], d['lat'])
            item = QTreeWidgetItem([d['display_name'], d['type']])
            item.setData(0, Qt.UserRole, geometry)
            if geometry.lower().startswith('point'):
                item.setIcon(0, QgsApplication.getThemeIcon('/mIconPointLayer.svg'))
            elif geometry.lower().startswith('linestring'):
                item.setIcon(0, QgsApplication.getThemeIcon('/mIconLineLayer.svg'))
            elif geometry.lower().startswith('polygon'):
                item.setIcon(0, QgsApplication.getThemeIcon('/mIconPolygonLayer.svg'))
            items.append(item)
        if items:
            self.location_search_dlg.eOutput.insertTopLevelItems(0, items)
            self.addSearchTerm(unicode(self.location_search_dlg.eText.text().lower()))
            self.location_search_dlg.search_result_lbl.setText(str(len(data)) + ' result')
        else:
            self.iface.messageBar().pushMessage('Nothing was found!', QgsMessageBar.CRITICAL, 2)
            self.location_search_dlg.search_result_lbl.setText('0 result')

    def itemChanged(self, current=None, previous=None):
        if current:
            wkt = str(current.data(0,Qt.UserRole))
            geom = QgsGeometry.fromWkt(wkt)
            if self.proj.srsid() != 4326:
                try:
                    geom.transform(self.transform)
                except:
                    self.iface.messageBar().pushMessage('CRS transformation error!', QgsMessageBar.CRITICAL, 2)
                    #self.rb.reset(QGis.Point)
                    return
            #self.rb.setToGeometry(geom, None)
            #if self.cbCenter.isChecked():
            self.moveCanvas(geom.centroid().asPoint(), self.canvas.extent())
            extent = viewport_geo_array(self.iface.mapCanvas())
            self.update_extent_ls(extent)
        else:
            #self.rb.reset(QGis.Point)
            self.location_search_dlg.eOutput.setCurrentItem(None)

    def crsChanged(self):
        self.proj = self.canvas.mapRenderer().destinationCrs()
        self.transform = QgsCoordinateTransform(self.wgs84, self.proj)

    def clearEdit(self):
        self.location_search_dlg.eOutput.clear()
        self.location_search_dlg.eText.clear()
        #if hasattr(self, 'rb'):
            #self.rb.reset(QGis.Point)
    
    def setCompleter(self):
        self.completer.model().setStringList(self.autocompleteList)
    
    def addSearchTerm(self, text):
        if not text in self.autocompleteList:
            self.autocompleteList.append(text)
            self.setCompleter()
        while len(self.autocompleteList) > self.searchCacheLimit:
            self.autocompleteList.pop(0)

    def autocenter(self, state):
        #if state and self.rb.size():
        #    self.moveCanvas(self.rb.asGeometry().centroid().asPoint(), self.canvas.extent())
        pass

    def moveCanvas(self, newCenter, oldExtent):
        newExtent = QgsRectangle(oldExtent)
        newExtent.scale(1, newCenter)
        self.canvas.setExtent(newExtent)
        self.canvas.zoomScale(4000)
        self.canvas.refresh()    

    def update_extent_ls(self, extent):
        """Update extent value in GUI based from an extent.
        :param extent: A list in the form [xmin, ymin, xmax, ymax] where all
            coordinates provided are in Geographic / EPSG:4326.
        :type extent: list
        """
        self.location_search_dlg.x_minimum.setValue(extent[0])
        self.location_search_dlg.y_minimum.setValue(extent[1])
        self.location_search_dlg.x_maximum.setValue(extent[2])
        self.location_search_dlg.y_maximum.setValue(extent[3])  

    def drag_rectangle_on_map_canvas(self):
        """Hide the dialog and allow the user to draw a rectangle."""

        self.location_search_dlg.hide()
        self.wizard_quickmap0_dlg.hide()
        self.rectangle_map_tool.reset()
        self.canvas.unsetMapTool(self.pan_tool)
        self.canvas.setMapTool(self.rectangle_map_tool)  
    
    def update_extent_from_rectangle(self):
        """Update extent value in GUI based from the QgsMapTool rectangle.

        .. note:: Delegates to update_extent()
        """
        self.wizard_quickmap0_dlg.show()
        self.location_search_dlg.show()
        self.canvas.unsetMapTool(self.rectangle_map_tool)
        self.canvas.setMapTool(self.pan_tool)

        rectangle = self.rectangle_map_tool.rectangle()
        if rectangle:
            self.location_search_dlg.bounding_box_group.setTitle(
                self.tr('Bounding box from rectangle'))
            extent = rectangle_geo_array(rectangle, self.iface.mapCanvas())
            self.update_extent_ls(extent) 

    def close_location_search(self):
        self.location_search_dlg.close()

    def show_building_osm(self):
        self.building_osm_dlg.show() 

    def show_road_osm(self):
        self.road_osm_dlg.show()  

    def close_building_osm(self):
        self.building_osm_dlg.close()
        
    def close_road_osm(self):
        self.road_osm_dlg.close() 

    def select_file_building(self):
        filepath = QFileDialog.getOpenFileName()
        self.building_osm_dlg.file_path_lineedit.setText(filepath) 

    def load_file_building(self):    
        if self.building_osm_dlg.osm_radio.isChecked() == False:
            filepath = self.building_osm_dlg.file_path_lineedit.text()
            extention_file = splitext(basename(filepath))[1]
            filename = splitext(basename(filepath))[0]
            if extention_file == ".shp" or extention_file == ".geojson" or extention_file == ".kml":
                layer = self.iface.addVectorLayer(filepath, filename, "ogr")
            elif extention_file == ".tif":    
                layer = self.iface.addRasterLayer(filepath, filename)
            else:
                QMessageBox.information(None, "Error:", str("Only shapefile, geojson, kml and tiff file is allowed"))
                
            if not layer:
                QMessageBox.information(None, "Error:", str("Only shapefile, geojson, kml and tiff file is allowed"))
            else:
                if self.wizard1_clicked:
                    self.check_impact_layer("Building",filename)
                self.building_osm_dlg.close()
        else:
            self.download_osm_building_on_wiz() 

        if self.wizard_clicked:
            self.wizard_quickmap_trigger()
        if self.wizard1_clicked:
            self.wizard_impact_trigger()     
            
    def select_file_road(self):
        filepath = QFileDialog.getOpenFileName()
        self.road_osm_dlg.file_path_lineedit.setText(filepath)

    def load_file_road(self):
        if self.road_osm_dlg.osm_radio.isChecked() == False:
            filepath = self.road_osm_dlg.file_path_lineedit.text()
            extention_file = splitext(basename(filepath))[1]
            filename = splitext(basename(filepath))[0]
            if extention_file == ".shp" or extention_file == ".geojson" or extention_file == ".kml":
                layer = self.iface.addVectorLayer(filepath, filename, "ogr")
            elif extention_file == ".tif":    
                layer = self.iface.addRasterLayer(filepath, filename)
            else:
                QMessageBox.information(None, "Error:", str("Only shapefile, geojson, kml and tiff file is allowed"))
                
            if not layer:
                QMessageBox.information(None, "Error:", str("Only shapefile, geojson, kml and tiff file is allowed"))
            else:
                self.road_osm_dlg.close()
        else:
            self.download_osm_road_on_wiz()

        if self.wizard_clicked:
            self.wizard_quickmap_trigger()
        if self.wizard1_clicked:
            self.wizard_impact_trigger() 

    def radio_building_click(self):
        if self.building_osm_dlg.osm_radio.isChecked():
            self.building_osm_dlg.browse_file_btn.setDisabled(True)
            self.building_osm_dlg.directory_button.setDisabled(False)
        else:
            self.building_osm_dlg.browse_file_btn.setDisabled(False)
            self.building_osm_dlg.directory_button.setDisabled(True)

    def building_dir_map(self):
        filepath = QFileDialog.getExistingDirectory()
        self.building_osm_dlg.output_directory.setText(filepath)         

    def radio_road_click(self):
        if self.road_osm_dlg.osm_radio.isChecked():
            self.road_osm_dlg.browse_file_btn.setDisabled(True)
            self.road_osm_dlg.directory_button.setDisabled(False)
        else:
            self.road_osm_dlg.browse_file_btn.setDisabled(False) 
            self.road_osm_dlg.directory_button.setDisabled(True)   

    def road_dir_map(self):
        filepath = QFileDialog.getExistingDirectory()
        self.road_osm_dlg.output_directory.setText(filepath)   
        
    def download_osm_road_on_wiz(self):
        try:
            extent = viewport_geo_array(self.iface.mapCanvas())
            feature_type = "roads"

            output_directory = self.road_osm_dlg.output_directory.text()
            output_prefix = ""
            overwrite = True
            output_base_file_path = self.get_output_base_path(
                output_directory, output_prefix, feature_type, overwrite)

            self.progress_dialog = QProgressDialog()
            self.progress_dialog.setAutoClose(False)
            title = self.tr('Road osm download')
            self.progress_dialog.setWindowTitle(title)

            # noinspection PyTypeChecker
            download(
                feature_type,
                output_base_file_path,
                extent,
                self.progress_dialog)

            try:
                self.load_shapefile(feature_type, output_base_file_path)
            except FileMissingError as exception:
                print exception.message
                QMessageBox.information(None, "Error:", str("Error download OSM data"))

        except CanceledImportDialogError:
            # don't show anything because this exception raised
            # when user canceling the import process directly
            pass
        except Exception as exception:  # pylint: disable=broad-except
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QMessageBox.information(None, "Error:", exception.message)

            self.progress_dialog.cancel()

        finally:
            # Unlock the bounding_box_group
            self.road_osm_dlg.close() 


    def download_osm_building_on_wiz(self):
        try:
            extent = viewport_geo_array(self.iface.mapCanvas())
            feature_type = "buildings"
            if self.wizard1_clicked:
                feature_type = "building-points"
                self.check_impact_layer("Building",feature_type)

            output_directory = self.building_osm_dlg.output_directory.text()
            output_prefix = ""
            overwrite = True
            output_base_file_path = self.get_output_base_path(
                output_directory, output_prefix, feature_type, overwrite)

            self.progress_dialog = QProgressDialog()
            self.progress_dialog.setAutoClose(False)
            title = self.tr('Road osm download')
            self.progress_dialog.setWindowTitle(title)

            # noinspection PyTypeChecker
            download(
                feature_type,
                output_base_file_path,
                extent,
                self.progress_dialog)

            try:
                self.load_shapefile(feature_type, output_base_file_path)
            except FileMissingError as exception:
                print exception.message
                QMessageBox.information(None, "Error:", str("Error download OSM data"))

        except CanceledImportDialogError:
            # don't show anything because this exception raised
            # when user canceling the import process directly
            pass
        except Exception as exception:  # pylint: disable=broad-except
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QMessageBox.information(None, "Error:", exception.message)

            self.progress_dialog.cancel()

        finally:
            # Unlock the bounding_box_group
            self.building_osm_dlg.close()               
            

    def get_output_base_path(
            self,
            output_directory,
            output_prefix,
            feature_type,
            overwrite):
        
        path = os.path.join(
            output_directory, '%s%s' % (output_prefix, feature_type))

        if overwrite:

            # If a shapefile exists, we must remove it (only the .shp)
            shp = '%s.shp' % path
            if os.path.isfile(shp):
                os.remove(shp)

        else:
            separator = '-'
            suffix = self.get_unique_file_path_suffix(
                '%s.shp' % path, separator)

            if suffix:
                path = os.path.join(output_directory, '%s%s%s%s' % (
                    output_prefix, feature_type, separator, suffix))

        return path 

    @staticmethod
    def get_unique_file_path_suffix(file_path, separator='-', i=0):
        basename = os.path.splitext(file_path)
        if i != 0:
            file_path_test = os.path.join(
                '%s%s%s%s' % (basename[0], separator, i, basename[1]))
        else:
            file_path_test = file_path

        if os.path.isfile(file_path_test):
            return OsmDownloaderDialog.get_unique_file_path_suffix(
                file_path, separator, i + 1)
        else:
            return i  

    def load_shapefile(self, feature_type, base_path):
        
        path = '%s.shp' % base_path

        if not os.path.exists(path):
            message = self.tr(
                '%s does not exist. The server does not have any data for '
                'this extent.' % path)
            raise FileMissingError(message)

        layer = self.iface.addVectorLayer(path, feature_type, 'ogr')

        # Check if it's a building layer and if it's QGIS 2.14 about the 2.5D
        if qgis_version() >= 21400 and feature_type == 'buildings':
            layer_scope = QgsExpressionContextUtils.layerScope(layer)
            if not layer_scope.variable('qgis_25d_height'):
                QgsExpressionContextUtils.setLayerVariable(
                    layer, 'qgis_25d_height', 0.0002)
            if not layer_scope.variable('qgis_25d_angle'):
                QgsExpressionContextUtils.setLayerVariable(
                    layer, 'qgis_25d_angle', 70)

        canvas_srid = self.canvas.mapSettings().destinationCrs().srsid()
        on_the_fly_projection = self.canvas.hasCrsTransformEnabled()
        if canvas_srid != 4326 and not on_the_fly_projection:
            if QGis.QGIS_VERSION_INT >= 20400:
                self.canvas.setCrsTransformEnabled(True)
            else:
                display_warning_message_bar(
                    self.iface,
                    self.tr('Enable \'on the fly\''),
                    self.tr(
                        'Your current projection is different than EPSG:4326. '
                        'You should enable \'on the fly\' to display '
                        'correctly your layers')
                )      

    def create_file_countries_download(self):
        json_str = "["
        i = 0
        total_data = len(self.country_list)
        for country in self.country_list:
            json_str = json_str + '{ "code1" : "'+country[0]+'", "country" : "'+country[1]+'", "code2" : "'+country[2]+'", "download" : "'+country[3]+'"}'
            i += 1
            if i != total_data:
                json_str = json_str + ','
        json_str = json_str + "]"            
        #{data : [{code1 : '', country : '', code2 : '', download : 'Y'}]}
        file = open(resources_path('webservice', 'countries.json'), 'w')
        file.write(json_str)
        file.close()

    def read_file_countries(self):
        json_data = open(resources_path('webservice', 'countries.json'))
        data = json.load(json_data)
        json_data.close()
        total_data = len(data)
        self.country_list = []
        for i in range(0,(total_data - 1)):
            self.country_list.append([data[i]["code1"],data[i]["country"],data[i]["code2"],data[i]["download"]])
            
    def country_downloader(self,country,country_prefix):
        try:
            output_directory = resources_path('countries_admin',country_prefix)
            
            self.progress_dialog = QProgressDialog()
            self.progress_dialog.setAutoClose(False)
            title = self.tr(country+' download')
            self.progress_dialog.setWindowTitle(title)

            # noinspection PyTypeChecker
            download_country(
                country_prefix,
                output_directory,
                self.progress_dialog)

            
            try:
                path_file = resources_path('countries_admin',country_prefix,country_prefix+'_adm0.shp')
                layer = QgsVectorLayer(path_file, country, 'ogr')
                #QgsMapLayerRegistry.instance().addMapLayers( [layer] )   

                country_list = []
                for country_ in self.country_list:
                    if country_[1] == country:
                        country_[2] = country_prefix
                        country_[3] = 'Y'
    
                    country_list.append(country_)   
                self.country_list = country_list
                self.create_file_countries_download()        
            except FileMissingError as exception:
                print exception.message
                QMessageBox.information(None, "Error:", str("Error download country"))
            
        except CanceledImportDialogError:
            # don't show anything because this exception raised
            # when user canceling the import process directly
            pass
        except Exception as exception:  # pylint: disable=broad-except
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QMessageBox.information(None, "Error:", str(exception.message))

            self.progress_dialog.cancel()

        finally:
            # Unlock the bounding_box_group
            pass  


    def countries_downloader(self):
        if os.path.exists(resources_path('countries_admin', 'ne_10m_admin_0_countries','ne_10m_admin_0_countries.shp')) == False:
            try:
                output_directory = resources_path('countries_admin','ne_10m_admin_0_countries')
                
                self.progress_dialog = QProgressDialog()
                self.progress_dialog.setAutoClose(False)
                title = self.tr('Countries Adm. download')
                self.progress_dialog.setWindowTitle(title)

                country = 'ne_10m_admin_0_countries'

                # noinspection PyTypeChecker
                download_country(
                    country,
                    output_directory,
                    self.progress_dialog)

            except CanceledImportDialogError:
                # don't show anything because this exception raised
                # when user canceling the import process directly
                pass
            except Exception as exception:  # pylint: disable=broad-except
                # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                QMessageBox.information(None, "Error:", str(exception.message))

                self.progress_dialog.cancel()

            finally:
                # Unlock the bounding_box_group
                pass

                  



              
    
        