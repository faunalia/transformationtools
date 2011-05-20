# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import QgsCoordinateReferenceSystem

class Transformation:

	def __init__(self, ID=None):
		if ID == "":
			ID = None
		self.ID = ID
		self.reloadData()

	def useGrid(self):
		return self.grid != None

	def useTowgs84(self):
		return self.towgs84 != None

	def useExtent(self):
		return self.extent != None

	def reloadData(self):
		if self.ID == None or not Transformation.exists( self.ID ):
			self.setDefaultPropValues()
			return False
		settings = QSettings()
		values = settings.value( u"/transformations/list/%s" % self.ID, QVariant([]) ).toList()
		self.setPropValues( map( lambda x: x.toString() if x.isValid() else None, values ) )
		return True
		
	def saveData(self):
		if self.name == None:
			return False
		settings = QSettings()
		if self.ID != self.name:
			self.deleteData()
		self.ID = self.name
		settings.setValue( u"/transformations/list/%s" % self.ID, QVariant( self.getPropValues() ) )
		return True

	def deleteData(self):
		if self.ID == None or not Transformation.exists( self.ID ):
			return False
		settings = QSettings()
		settings.remove( u"/transformations/list/%s" % self.ID )
		return True

	@staticmethod
	def exists(ID):
		settings = QSettings()
		return settings.contains( u"/transformations/list/%s" % ID )

	@staticmethod
	def getById(ID):
		if not Transformation.exists( ID ):
			return None
		return Transformation( ID )

	@staticmethod
	def getByCrs(inCrs, outCrs, enabledOnly=False):
		sameCrs = []
		for t in Transformation.getAll():
			crs = t.getInputCrs()
			if not crs.isValid() or crs != inCrs:
				continue
			crs = t.getOutputCrs()
			if not crs.isValid() or crs != outCrs:
				continue
			if not enabledOnly or t.enabled:
				sameCrs.append( t )
		return sameCrs


	@staticmethod
	def getAll(enabledOnly=False):
		transformations = []
		settings = QSettings()
		settings.beginGroup( "/transformations/list/" )
		keys = settings.childKeys()
		for ID in keys:
			t = Transformation(ID)
			if not enabledOnly or t.enabled:
				transformations.append( t )
		settings.endGroup()
		return transformations

	def getPropValues(self):
		return [ self.name, self.inCrs, self.outCrs, self.grid, self.towgs84, self.extent, self.inCustomCrsName, self.outCustomCrsName, self.enabled ]

	def setPropValues(self, values):
		self.name, self.inCrs, self.outCrs, self.grid, self.towgs84, self.extent, self.inCustomCrsName, self.outCustomCrsName, self.enabled = values

	def setDefaultPropValues(self):
		self.setPropValues([None]*9)

	def getInputCrs(self):
		return QgsCoordinateReferenceSystem( self.inCrs )

	def getOutputCrs(self):
		return QgsCoordinateReferenceSystem( self.outCrs )

	def getInputCustomCrs(self):
		crs = self.getInputCrs()
		if self.useGrid():
			crs.createFromProj4( "%s +nadgrids=%s +wktext" % (crs.toProj4(), self.grid) )
		elif self.useTowgs84():
			crs.createFromProj4( "%s +towgs84=%s +wktext" % (crs.toProj4(), self.towgs84) )
		return crs

	def getOutputCustomCrs(self):
		crs = self.getOutputCrs()
		if self.useGrid() or self.useTowgs84():
			crs.createFromProj4( "%s +towgs84=0,0,0 +wktext" % crs.toProj4() )
		return crs

