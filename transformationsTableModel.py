# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import qgis
from pyspatialite import dbapi2 as sqlite

from transformations import Transformation

class TransformationsTableModel(QAbstractTableModel):

	def __init__(self, parent=None, enabledOnly=False, manageEnabled=True):
		QAbstractTableModel.__init__(self, parent)
		self.header = ( "Name", "Input CRS", "Output CRS", "Params" )

		self.manageEnabled = manageEnabled
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
		t = self.getAtRow( index.row() )

		if not self.enabledOnly and role == Qt.CheckStateRole and index.column() == 0:
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
					val = "towgs84=%s" % t.towgs84
				elif t.useGrid():
					val = "grid=%s" % t.grid
			return QVariant(val) if val != None else QVariant()

		return QVariant()

	def setData(self, index, value, role):
		if not index.isValid():
			return False
		if self.manageEnabled and role == Qt.CheckStateRole:
			t = self.getAtRow( index.row() )
			t.enabled = value == Qt.Checked
			t.saveData()
			return True
		return False
		
	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < self.columnCount():
			return QVariant(self.header[section])
		return QVariant()

class FilteredTransformationsTableModel(TransformationsTableModel):
	def __init__(self, inCrs, outCrs, parent=None, enabledOnly=False, manageEnabled=True):
		self.inCrs = inCrs
		self.outCrs = outCrs
		TransformationsTableModel.__init__(self, parent, enabledOnly, manageEnabled)

	def reloadData(self):
		self.transformations = Transformation.getByCrs(self.inCrs, self.outCrs, self.enabledOnly)
		self.row_count = len(self.transformations)

