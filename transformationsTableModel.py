# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : Transformation tools
Description          : Help to use grids and towgs84 to transform a vector/raster
Date                 : April 16, 2011 
copyright            : (C) 2011 by Giuseppe Sucameli (Faunalia)
email                : brush.tyler@gmail.com

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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import qgis
from pyspatialite import dbapi2 as sqlite

from transformations import Transformation

class TransformationsTableModel(QAbstractTableModel):

	def __init__(self, parent=None, enabledOnly=False, manageEnabled=True):
		QAbstractTableModel.__init__(self, parent)
		self.header = ( "Name", "CRS A", "CRS B", "Grid or params" )

		self.manageEnabled = False #manageEnabled
		self.enabledOnly = enabledOnly

		self.row_count = 0
		self.col_count = len( self.header )
		if self.col_count == 0:
			return

		self.reloadData()

	def reloadData(self):
		self.transformations = Transformation.getAll( self.enabledOnly )
		self.row_count = len(self.transformations)

	def getAtRow(self, row):
		return self.transformations[row]

	def rowCount(self, index=None):
		return self.row_count

	def columnCount(self, index=None):
		return self.col_count

	def flags(self, index):
		if not index.isValid():
			return 0
		flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
		if self.manageEnabled and index.column() == 0:
			flags |= Qt.ItemIsUserCheckable
		return flags

	def data(self, index, role):
		if not index.isValid():
			return QVariant()
		t = self.transformations[ index.row() ]

		if self.manageEnabled and not self.enabledOnly and role == Qt.CheckStateRole and index.column() == 0:
			return Qt.Checked if t.enabled else Qt.Unchecked

		if role == Qt.DisplayRole:
			val = None
			if index.column() == 0:
				val = t.name
			elif index.column() == 1:
				val = t.inCrs
			elif index.column() == 2:
				val = t.outCrs
			elif index.column() == 3:
				if t.useTowgs84():
					val = "towgs84=%s" % t.inTowgs84
				elif t.useGrid():
					val = "grid=%s" % t.inGrid
			return QVariant(val) if val != None else QVariant()

		return QVariant()

	def setData(self, index, value, role):
		if not index.isValid():
			return False
		if self.manageEnabled and role == Qt.CheckStateRole:
			t = self.transformations[ index.row() ]
			t.enabled = value == Qt.Checked
			t.saveData()
			return True
		return False
		
	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < self.columnCount():
			return QVariant(self.header[section])
		return QVariant()

class FilteredTransformationsTableModel(TransformationsTableModel):
	def __init__(self, crsA, crsB, parent=None, enabledOnly=False, manageEnabled=True):
		self.crsA = crsA
		self.crsB = crsB
		TransformationsTableModel.__init__(self, parent, enabledOnly, manageEnabled)

	def reloadData(self):
		res = Transformation.getByCrs(self.crsA, self.crsB, self.enabledOnly, True)
		self.transformations = map( lambda x: x[0], res )
		self.isInverse = map( lambda x: x[1], res )

		self.row_count = len(self.transformations)

	def getAtRow(self, row):
		return self.transformations[row], self.isInverse[row]

