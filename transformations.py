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

	fields = ['id', 'name', 'incrs', 'outcrs', 'grid', 'towgs84', 'extent', 'newincrsname', 'newoutcrsname', 'enabled']

	def __init__(self, ID=None):
		self.__setDefaultPropValues()
		self.id = ID
		self.reloadData()

	@staticmethod
	def createFromPropValues(props):
		t = Transformation(None)
		t.__setPropValues(props)
		return t


	def __getPropValues(self):
		props = []
		[ props.append( getattr(self, f, None) ) for f in Transformation.fields ]
		return props

	def __setPropValues(self, values):
		for k, v in values.iteritems():
			if k in Transformation.fields:
				if k == 'enabled':
					v = v == None or ( str(v).lower() != 'false' and str(v).lower() != '0' and v )
				setattr(self, k, v)

	def __setDefaultPropValues(self):
		self.__setPropValues( dict(zip(Transformation.fields, [None]*len(Transformation.fields))) )

	@classmethod
	def __getCursor(self):
		dbpath = QgsApplication.qgisUserDbFilePath()
		if not hasattr(Transformation, '__connection'):
			try:
				Transformation.__connection = sqlite.connect( unicode(dbpath).encode('utf8') )
			except sqlite.OperationalError, e:
				QMessageBox.critical( None, u"Error opening the database", u"Can't open the database %s: %s" % (dbpath, e.args[0]) )
				return

		return Transformation.__connection.cursor()

	@staticmethod
	def __execute(sql, params=None, cursor=None, commitWhenCursor=False):
		autoCommit = cursor == None or commitWhenCursor
		if cursor == None:
			cursor = Transformation.__getCursor()
			if cursor == None:
				return False

		try:
			cursor.execute( sql, params if params != None else [] )
		except sqlite.OperationalError:
			Transformation.__connection.rollback()
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
				incrs varchar(255) NOT NULL,
				outcrs varchar(255) NOT NULL,
				grid varchar(255) NULL,
				towgs84 varchar(255) NULL,
				extent varchar(255) NULL,
				newincrsname varchar(255) NOT NULL,
				newincrs_id varchar(255) NULL,
				newoutcrsname varchar(255) NOT NULL,
				newoutcrs_id varchar(255) NULL,
				enabled varchar(1) NOT NULL default 't'
			)"""
		return Transformation.__execute( sql )


	def useGrid(self):
		return self.grid != None

	def useTowgs84(self):
		return self.towgs84 != None

	def useExtent(self):
		return self.extent != None


	def reloadData(self):
		if self.id == None or not Transformation.exists( self.id ):
			return False

		fields = Transformation.fields[1:]
		sql = u"SELECT %s FROM tbl_transformation WHERE id=?" % ( ','.join(fields) )
		Transformation.__execute( sql, [self.id] )
		self.__setPropValues( dict(zip(fields, cursor.fetchone())) )
		return True
		
	def saveData(self):
		# this will add both CRSs to the tbl_srs table (done by QgsCoordinateReferenceSystem)
		newinproj = self.getInputCustomCrs().toProj4()
		newoutproj = self.getOutputCustomCrs().toProj4()

		cursor = Transformation.__getCursor()
		if cursor == None:
			return False

		# don't take care about the id field, convert all params to strings
		fields = Transformation.fields[1:]
		params = map( lambda x: unicode(x) if x != None else None, self.__getPropValues()[1:] )
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

		# update the both input and output custom CRS
		params = [ unicode(newinproj) ]
		sql = u"SELECT srs_id FROM tbl_srs WHERE parameters=? ORDER BY srs_id DESC LIMIT 1"
		Transformation.__execute( sql, params, cursor )
		row = cursor.fetchone()
		if row != None:
			params = [ unicode(self.newincrsname), unicode(row[0]) ]
			sql = u"UPDATE tbl_srs SET description=? WHERE srs_id=?"
			Transformation.__execute( sql, params, cursor )
		else:
			qWarning(u">>> NO input crs record found??")


		params = [ unicode(newoutproj) ]
		sql = u"SELECT srs_id FROM tbl_srs WHERE parameters=? ORDER BY srs_id DESC LIMIT 1"
		Transformation.__execute( sql, params, cursor )
		row = cursor.fetchone()
		if row != None:
			params = [ unicode(self.newoutcrsname), unicode(row[0]) ]
			sql = u"UPDATE tbl_srs SET description=? WHERE srs_id=?"
			Transformation.__execute( sql, params, cursor )
		else:
			qWarning(u">>> NO output crs record found??")

		Transformation.__connection.commit()
		return True

	def deleteData(self):
		if self.id == None:
			return False

		# this will add both CRSs to the tbl_srs table (done by QgsCoordinateReferenceSystem)
		newinproj = self.getInputCustomCrs().toProj4()
		newoutproj = self.getOutputCustomCrs().toProj4()

		cursor = Transformation.__getCursor()
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
		cursor = Transformation.__getCursor()
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
	def getByCrs(inCrs, outCrs, enabledOnly=False):
		allTransformations = Transformation.getAll(enabledOnly)
		if allTransformations == None:
			return

		sameCrs = []
		for t in allTransformations:
			# check for the same input crs
			baseincrs = t.__getInputCrs()
			if not baseincrs.isValid() or baseincrs != inCrs:
				continue

			# check for the same output crs or custom output crs
			baseoutcrs = t.__getOutputCrs()
			newoutcrs = t.getOutputCustomCrs()
			if not (baseoutcrs.isValid() and outCrs == baseoutcrs) and not (newoutcrs.isValid() and outCrs == newoutcrs):
				continue

			sameCrs.append( t )
		return sameCrs


	@staticmethod
	def getAll(enabledOnly=False):
		cursor = Transformation.__getCursor()
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

	def __getInputCrs(self):
		crs = QgsCoordinateReferenceSystem( self.incrs )
		if not crs.isValid():
			if not crs.createFromProj4( self.incrs ):
				qWarning( u"unable to create the output CRS from '%s'" % self.incrs )
		return crs

	def __getOutputCrs(self):
		crs = QgsCoordinateReferenceSystem( self.outcrs )
		if not crs.isValid():
			if not crs.createFromProj4( self.outcrs ):
				qWarning( u"unable to create the output CRS from '%s'" % self.outcrs )
		return crs

	def getInputCustomCrs(self):
		crs = self.__getInputCrs()
		if self.useGrid():
			proj4 = self.__removeFromProj4(crs.toProj4(), ['+towgs84'])
			proj4 = self.__addToProj4(proj4, {'+nadgrids':self.grid, '+wktext':None})
			crs.createFromProj4( proj4 )
		elif self.useTowgs84():
			proj4 = self.__removeFromProj4(crs.toProj4(), ['+nadgrids'])
			proj4 = self.__addToProj4(proj4, {'+towgs84':self.towgs84, '+wktext':None})
			crs.createFromProj4( proj4 )
		return crs

	def getOutputCustomCrs(self):
		crs = self.__getOutputCrs()
		if self.useGrid() or self.useTowgs84():
			proj4 = self.__removeFromProj4(crs.toProj4(), ['+nadgrids'])
			proj4 = self.__addToProj4(proj4, {'+towgs84':'0,0,0', '+wktext':None})
			crs.createFromProj4( proj4 )
		return crs

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
			rxstr = "\s%s(?:\=\S+)?%s"  % ( QRegExp.escape(k), '\\b' )
			proj4 = QString(proj4).remove( QRegExp(rxstr) )
		return proj4


# create the table on qgis.db if not exists yet
Transformation.createTable()

