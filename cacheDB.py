# -*- coding: utf-8 -*-
"""
/***************************************************************************
 osmSearchDialog
                                 A QGIS plugin
 Search OpenStreetMap data by name or address using Nominating service
                              -------------------
        begin                : 2013-03-29
        copyright            : (C) 2013 by Piotr Pociask
        email                : piotr.pociask (at) gis-support (dot) pl
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
 
import sqlite3 as sql
from PyQt4.QtCore import QFileInfo
from PyQt4.QtGui import QMessageBox

class cacheDB(object):
    def __init__(self):
        self.dbFile = str(QFileInfo(__file__).absolutePath())+'/cache.db'
        self.conn = None
        self.checkTables()
    
    def openConnection(self):
        self.conn = sql.connect(self.dbFile)
        self.cursor = self.conn.cursor()
    
    def closeConnection(self):
        if self.conn:
            self.conn.close()
    
    def checkTables(self):
        if not self.conn:
            self.openConnection()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS autocomplete (value TEXT NOT NULL, UNIQUE(value) ON CONFLICT IGNORE)")
        self.conn.commit()
    
    def addAutocomplete(self, value):
        if not self.conn:
            self.openConnection()
        self.cursor.execute("INSERT INTO autocomplete VALUES ('%s')" % value)
        self.conn.commit()
    
    def addAutocompleteList(self, values):
        if not self.conn:
            self.openConnection()
        self.cursor.execute("DELETE FROM autocomplete")
        for value in values:
            self.cursor.execute("INSERT INTO autocomplete VALUES ('%s')" % value)
        self.conn.commit()
    
    def getAutocompleteList(self):
        if not self.conn:
            self.openConnection()
        self.cursor.execute("SELECT * FROM autocomplete")
        rows = self.cursor.fetchall()
        return [x[0] for x in rows]