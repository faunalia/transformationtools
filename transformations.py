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

from qgis.core import QgsApplication, 	QgsCoordinateReferenceSystem
from pyspatialite import dbapi2 as sqlite

class Transformation:

	fields = ['id', 'name', 'inCrs', 'outCrs', 'inGrid', 'inTowgs84', 'outTowgs84', 'extent', 'newInCrsName', 'newOutCrsName', 'enabled']

	def __init__(self, ID=None):
		self._setDefaultPropValues()
		self.id = ID
		self.reloadData()

	@staticmethod
	def createFromPropValues(props):
		t = Transformation(None)
		t._setPropValues(props)
		return t


	def _getPropValues(self):
		props = []
		[ props.append( getattr(self, f, None) ) for f in Transformation.fields ]
		return props

	def _setPropValues(self, values):
		for k, v in values.iteritems():
			if k in Transformation.fields:
				if k == 'enabled':
					v = v == None or ( str(v).lower() != 'false' and str(v).lower() != '0' and v )
				setattr(self, k, v)

	def _setDefaultPropValues(self):
		self._setPropValues( dict(zip(Transformation.fields, [None]*len(Transformation.fields))) )

	@classmethod
	def _getCursor(self):
		dbpath = QgsApplication.qgisUserDbFilePath()
		if not hasattr(Transformation, '__connection'):
			try:
				Transformation.__connection = sqlite.connect( unicode(dbpath).encode('utf8') )
			except sqlite.OperationalError, e:
				QMessageBox.critical( None, u"Error opening the database", u"Can't open the database %s: %s" % (dbpath, e.args[0]) )
				return

		return Transformation.__connection.cursor()

	@staticmethod
	def __execute(sql, params=None, cursor=None, forceCommit=False):
		autoCommit = cursor == None or forceCommit
		if cursor == None:
			cursor = Transformation._getCursor()
			if cursor == None:
				return False

		try:
			cursor.execute( sql, params if params != None else [] )
		except sqlite.OperationalError:
			del cursor
			Transformation.__connection.rollback()
			Transformation.__connection = None
			raise

		if autoCommit:
			Transformation.__connection.commit()
		return True

	@staticmethod
	def createTable(drop=False):

		if drop:
			sql = u"""DROP TABLE IF EXISTS tbl_transformation"""
			Transformation.__execute( sql )

		sql = u"""CREATE TABLE IF NOT EXISTS tbl_transformation (
				id integer PRIMARY KEY,
				name varchar(255) NOT NULL,
				inCrs varchar(255) NOT NULL,
				inGrid varchar(255) NULL,
				inTowgs84 varchar(255) NULL,
				outCrs varchar(255) NOT NULL,
				outTowgs84 varchar(255) NULL,
				extent varchar(255) NULL,
				newInCrsName varchar(255) NULL,
				newInCrsId varchar(255) NULL,
				newOutCrsName varchar(255) NULL,
				newOutCrsId varchar(255) NULL,
				enabled varchar(1) NOT NULL default 't'
			)"""
		return Transformation.__execute( sql )


	def __eq__(self, other):
		if not isinstance(other, Transformation):
			return False
		if self.id == other.id:
			return True
		return False


	def useGrid(self):
		return self.inGrid != None

	def useTowgs84(self):
		return self.inTowgs84 != None

	def useExtent(self):
		return self.extent != None


	def reloadData(self):
		if self.id == None or not Transformation.exists( self.id ):
			return False

		fields = Transformation.fields[1:]
		sql = u"SELECT %s FROM tbl_transformation WHERE id=?" % ( ','.join(fields) )
		Transformation.__execute( sql, [self.id] )
		self._setPropValues( dict(zip(fields, cursor.fetchone())) )
		return True
		
	def saveData(self):
		newincrs = self._getInputCustomCrs()
		newoutcrs = self._getOutputCustomCrs()

		# this will add not already known CRSs to the tbl_srs table
		newinproj = newincrs.toProj4()
		newoutproj = newoutcrs.toProj4()

		cursor = Transformation._getCursor()
		if cursor == None:
			return False

		# update the both input and output custom CRS
		if self.newInCrsName != None:
			params = [ unicode(newinproj) ]
			sql = u"SELECT srs_id FROM tbl_srs WHERE parameters=? ORDER BY srs_id DESC LIMIT 1"
			Transformation.__execute( sql, params, cursor )
			row = cursor.fetchone()
			if row != None:
				params = [ unicode(self.newInCrsName), unicode(row[0]) ]
				sql = u"UPDATE tbl_srs SET description=? WHERE srs_id=?"
				Transformation.__execute( sql, params, cursor )
			else:
				self.newInCrsName = None

		if self.newOutCrsName != None:
			params = [ unicode(newoutproj) ]
			sql = u"SELECT srs_id FROM tbl_srs WHERE parameters=? ORDER BY srs_id DESC LIMIT 1"
			Transformation.__execute( sql, params, cursor )
			row = cursor.fetchone()
			if row != None:
				params = [ unicode(self.newOutCrsName), unicode(row[0]) ]
				sql = u"UPDATE tbl_srs SET description=? WHERE srs_id=?"
				Transformation.__execute( sql, params, cursor )
			else:
				self.newOutCrsName = None

		# don't take care about the id field, convert all params to strings
		fields = Transformation.fields[1:]
		params = map( lambda x: unicode(x) if x != None else None, self._getPropValues()[1:] )
		if self.id == None:
			# insert as new transformation
			sql = u"INSERT INTO tbl_transformation (%s) VALUES (%s)" % ( ','.join(fields), ','.join(['?']*len(fields)) )
			Transformation.__execute( sql, params, cursor )
			self.id = cursor.lastrowid
		else:
			# update the transformation
			sql = u"UPDATE tbl_transformation SET %s WHERE id=?" % ( '=?,'.join(fields) + '=?' )
			params.append( self.id )
			Transformation.__execute( sql, params, cursor )

		Transformation.__connection.commit()
		return True

	def deleteData(self):
		if self.id == None:
			return False

		# this will add both CRSs to the tbl_srs table (done by QgsCoordinateReferenceSystem)
		newinproj = self._getInputCustomCrs().toProj4()
		newoutproj = self._getOutputCustomCrs().toProj4()

		cursor = Transformation._getCursor()
		if cursor == None:
			return False

		# delete the input custom CRS
		params = [ unicode(newinproj) ]
		sql = u"SELECT srs_id FROM tbl_srs WHERE parameters=? ORDER BY srs_id DESC LIMIT 1"
		Transformation.__execute( sql, params, cursor )
		row = cursor.fetchone()
		if row != None:
			params = [ unicode(row[0]) ]
			sql = u"DELETE FROM tbl_srs WHERE srs_id=?"
			Transformation.__execute( sql, params, cursor )

		# delete the output custom CRS
		params = [ unicode(newoutproj) ]
		sql = u"SELECT srs_id FROM tbl_srs WHERE parameters=? ORDER BY srs_id DESC LIMIT 1"
		Transformation.__execute( sql, params, cursor )
		if row != None:
			params = [ unicode(row[0]) ]
			sql = u"DELETE FROM tbl_srs WHERE srs_id=?"
			Transformation.__execute( sql, params, cursor )

		sql = u"DELETE FROM tbl_transformation WHERE id=?"
		Transformation.__execute( sql, [self.id], cursor )

		Transformation.__connection.commit()
		return True


	@staticmethod
	def exists(ID):
		cursor = Transformation._getCursor()
		if cursor == None:
			return

		sql = u"SELECT count(*) > 0 FROM tbl_transformation WHERE id=?"
		ret = Transformation.__execute( sql, [ID], cursor, True )
		if not ret: return
		return cursor.fetchone()[0] == 't'

	@staticmethod
	def getById(ID):
		if ID == None or not Transformation.exists( ID ): 
			return
		return Transformation( ID )

	@staticmethod
	def getByCrs(crsA, crsB, enabledOnly=False, alsoInverse=False):
		allTransformations = Transformation.getAll(enabledOnly)
		if allTransformations == None:
			return

		sameCrs = []
		for t in allTransformations:
			# check for the direct transformation: crsA = inputCrs and crsB = outputCrs
			if t.isApplicableTo( crsA, crsB ):
				sameCrs.append( (t, False) )
				continue

			if not alsoInverse:
				continue

			# check for the inverse transformation: crsA = outputCrs and crsB = inputCrs
			if t.isApplicableTo( crsB, crsA ):
				sameCrs.append( (t, True) )
				continue

		return sameCrs


	@staticmethod
	def getAll(enabledOnly=False):
		cursor = Transformation._getCursor()
		if cursor == None: 
			return

		params = []
		sql = u"SELECT %s FROM tbl_transformation" % ( ','.join(Transformation.fields) )
		if enabledOnly: 
			sql += " WHERE enabled=?"
			params.append( 'True' )
		Transformation.__execute( sql, params, cursor )

		transformations = []
		for values in cursor.fetchall():
			t = Transformation.createFromPropValues( dict(zip(Transformation.fields, values)) )
			transformations.append( t )
		return transformations


	def isApplicableTo(self, crsA, crsB, skipIfApplied=True):
		if self._sameBaseInputCrs( crsA ) and self._sameBaseOutputCrs( crsB ):
			if crsA == self.getInputCustomCrs() and crsB == self.getOutputCustomCrs():
				# already applied
				return True if not skipIfApplied else False
			return True
		return False


	def _sameBaseInputCrs(self, crs):
		incrs = self._getInputCrs()
		if crs == incrs:	# it's the same
			return True

		# remove towgs84, nadgrids and wktext from both and try again
		newcrs = QgsCoordinateReferenceSystem()
		inproj4 = self.__removeFromProj4(incrs.toProj4(), ['+towgs84', '+nadgrids', '+wktext'])
		newproj4 = self.__removeFromProj4(crs.toProj4(), ['+towgs84', '+nadgrids', '+wktext'])
		if incrs.createFromProj4( inproj4 ) and incrs.isValid() and \
				newcrs.createFromProj4( newproj4 ) and newcrs.isValid():
			if newcrs == incrs:
				return True

		return False

	def _sameBaseOutputCrs(self, crs):
		outcrs = self._getOutputCrs()
		if crs == outcrs:	# it's the same
			return True

		# remove towgs84, nadgrids and wktext from both and try again
		newcrs = QgsCoordinateReferenceSystem()
		outproj4 = self.__removeFromProj4(outcrs.toProj4(), ['+towgs84', '+nadgrids', '+wktext'])
		newproj4 = self.__removeFromProj4(crs.toProj4(), ['+towgs84', '+nadgrids', '+wktext'])
		if outcrs.createFromProj4( outproj4 ) and outcrs.isValid() and \
				newcrs.createFromProj4( newproj4 ) and newcrs.isValid():
			if newcrs == outcrs:
				return True

		return False

	def _getInputCrs(self):
		crs = QgsCoordinateReferenceSystem( self.inCrs )
		if not crs.isValid():
			if not crs.createFromProj4( self.inCrs ):
				qWarning( u"unable to create the output CRS from '%s'" % self.inCrs )
		return crs

	def _getOutputCrs(self):
		crs = QgsCoordinateReferenceSystem( self.outCrs )
		if not crs.isValid():
			if not crs.createFromProj4( self.outCrs ):
				qWarning( u"unable to create the output CRS from '%s'" % self.outCrs )
		return crs


	def _getInputCustomCrs(self):
		crs = self._getInputCrs()
		if self.useGrid():
			proj4 = self.__removeFromProj4(crs.toProj4(), ['+towgs84'])
			proj4 = self.__addToProj4(proj4, {'+nadgrids':self.inGrid, '+wktext':None})
			crs.createFromProj4( proj4 )
		elif self.useTowgs84():
			proj4 = self.__removeFromProj4(crs.toProj4(), ['+nadgrids'])
			proj4 = self.__addToProj4(proj4, {'+towgs84':self.inTowgs84, '+wktext':None})
			crs.createFromProj4( proj4 )
		return crs

	def _getOutputCustomCrs(self):
		crs = self._getOutputCrs()
		if self.useGrid() or self.useTowgs84():
			proj4 = self.__removeFromProj4(crs.toProj4(), ['+nadgrids'])

			# try to avoid duplicated CRSs

			if False and self.outTowgs84 != None:	# TODO self.ouTowgs84 not supported
				# if a new towgs84 param value was defined
				proj4 = self.__addToProj4(proj4, {'+towgs84':self.outTowgs84, '+wktext':None})
				crs.createFromProj4( proj4 )

			else: 
				# either datum or towgs84 is required
				towgs84 = self.__valueIntoProj4(proj4, '+towgs84')

				if towgs84 == None:
					if not self.__existIntoProj(proj, '+datum'):
						proj4 = self.__addToProj4(proj4, {'+towgs84':'0,0,0', '+wktext':None})
						crs.createFromProj4( proj4 )

				else:
					# check if towgs84 param has zero values only
					for x in towgs84.split(','):
						# both 0 (int) and 0.000... (float) are valid values 
						try:
							x = float(x)
						except ValueError:
							x = None
						if x != 0:
							towgs84 = None
							break

					# if towgs84 param has some values different from zero
					if towgs84 == None:
						proj4 = self.__addToProj4(proj4, {'+towgs84':'0,0,0', '+wktext':None})
						crs.createFromProj4( proj4 )
		return crs


	def getInputCustomCrs(self, inverseTransformation=False):
		return self._getInputCustomCrs() if not inverseTransformation else self._getOutputCustomCrs()

	def getOutputCustomCrs(self, inverseTransformation=False):
		return self._getOutputCustomCrs() if not inverseTransformation else self._getInputCustomCrs()


	def __existIntoProj4(self, proj4, param):
		return self.__valueIntoProj4(proj4, param) != None

	def __valueIntoProj4(self, proj4, param):
		rxstr = "\s%s(?:\=(\S+))?\\b"  % QRegExp.escape(param)
		regex = QRegExp(rxstr)
		if regex.indexIn( proj4 ) < 0:
			return None
		if regex.pos(1) < 0:
			return ""
		return regex.cap(1)

	def __addToProj4(self, proj4, params=None):
		if params == None:
			return proj4
		proj4 = self.__removeFromProj4(proj4, params.keys())
		for k, v in params.iteritems():
			newstr = " %s=%s" % (k,v) if v != None else " %s" % k
			proj4 = QString(proj4).append( newstr )
		return proj4

	def __removeFromProj4(self, proj4, params=None):
		if params == None:
			return proj4
		for k in params:
			rxstr = "\s%s(?:\=\S+)?\\b"  % QRegExp.escape(k)
			proj4 = QString(proj4).remove( QRegExp(rxstr) )
		return proj4



# create the table on qgis.db if not exists yet
dropNow = False
vers_with_db_changes = ['', '0.0.3']

settings = QSettings("/Transformation_Tools")
#settings.setValue("/last_version", "")

last_version = settings.value("/last_version", "").toString()
import TransformationTools
new_version = TransformationTools.version()
if last_version != new_version:
	settings.setValue("/last_version", new_version)
	if last_version in vers_with_db_changes:
		dropNow = True

Transformation.createTable(dropNow)
