This plugin is originally from InaSAFE (http://www.inasafe.org), especially for OSM downloader and Map Composer.
We added functions to download data from WMS/WFS/WCS and created simple analysis for affected building/population.


System Requirements
-------------------

 - A standard PC with at least 4GB of RAM running Windows, Linux or Mac OS X
 - The QGIS Open Source Geographic Information System (http://www.qgis.org).

Installation 
-------------------

with Ubuntu.

 1. install QGIS first. : https://www.qgis.org/en/site/forusers/alldownloads.html#debian-ubuntu
 2. install qt : http://wiki.qt.io/Install_Qt_5_on_Ubuntu
 3. install pip : sudo apt install python-pip
 4. install sip : https://pypi.python.org/pypi/SIP/4.19 - pip install sip
 5. install pyqt : http://www.saltycrane.com/blog/2008/01/how-to-install-pyqt4-on-ubuntu-linux/
 6. install pyrcc4 : sudo apt install pyqt4-dev-tools
 7. install git : sudo apt install git

=======
 
If you have problem with installing SIP you can do manually by download the source first from https://www.riverbankcomputing.com/software/sip/download/
and then install it with make install 

Clone git repository
-------------------

### Dependencies

The Graphical User Interface components are built using
`PyQt4 <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_ and the QGIS
plugin API (useful resources: `the QGIS Python Cookbook
<http://qgis.org/pyqgis-cookbook/>`_ and `the QGIS C++ API documentation
<http://qgis.org/api/>`_). As such it is helpful if you are familiar with these
technologies (python, Qt4, PyQt4, QGIS). In addition, the following are needed
on your machine in order to work effectively with the code base:

* git
* rsync
* pep8
* nosetests (with coverage plugin)
* python-numpy (for numerical computations)
* python-gdal (python bindings to underlying gis functionality)
* python-sphinx (compilation of documents)
* cloud-sptheme (sphinx theme)
* pyqt4-dev-tools (compiling ui and resources)
* qt4-doc (qt4 API documentation)
* pyflakes (test for bad coding style like unused imports / vars)
* python-nosexcover and python-coverage (code coverage reporting)

On an ubuntu system you can install these requirements using apt::

   sudo apt-get install git rsync pep8 python-nose python-coverage python-gdal python-numpy python-sphinx pyqt4-dev-tools pyflakes python-nosexcover

In some cases these dependencies may already be on your system via installation
process you followed for QGIS.

### Cloning the source code from git

To develop on the plugin, you first need to copy it to your local system. If
you are a developer, the simplest way to do that is go to
:file:`~/.qgis2/python/plugins` and clone |project_name| from our GitHub
repository page like this::
 
 1. mkdir SaVap
 2. cd SaVap
 3. sudo git init
 4. sudo git remote add origin git@203.159.29.222:bayu/qgis_plugin_adb_sa.git
 5. sudo git pull origin master
 6. sudo git checkout develop

 
License
=======

Emergency Mapper is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License version 3 (GPLv3) as
published by the Free Software Foundation.

The full GNU General Public License is available in LICENSE.txt or
http://www.gnu.org/licenses/gpl.html


Disclaimer of Warranty (GPLv3)
==============================

There is no warranty for the program, to the extent permitted by
applicable law. Except when otherwise stated in writing the copyright
holders and/or other parties provide the program "as is" without warranty
of any kind, either expressed or implied, including, but not limited to,
the implied warranties of merchantability and fitness for a particular
purpose. The entire risk as to the quality and performance of the program
is with you. Should the program prove defective, you assume the cost of
all necessary servicing, repair or correction.


Limitation of Liability (GPLv3)
===============================

In no event unless required by applicable law or agreed to in writing
will any copyright holder, or any other party who modifies and/or conveys
the program as permitted above, be liable to you for damages, including any
general, special, incidental or consequential damages arising out of the
use or inability to use the program (including but not limited to loss of
data or data being rendered inaccurate or losses sustained by you or third
parties or a failure of the program to operate with any other programs),
even if such holder or other party has been advised of the possibility of
such damages.

Thank you
