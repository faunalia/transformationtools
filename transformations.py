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
		if self.hasSameInputCrsBase( crsA ) and self.hasSameOutputCrsBase( crsB ):
			if crsA == self.getInputCustomCrs() and crsB == self.getOutputCustomCrs():
				# already applied
				return True if not skipIfApplied else False
			return True
		return False


	def sameBaseCrs(self, crs1, crs2):
		if crs1 == crs2:	# it's the same!
			return True

		# remove towgs84, nadgrids and wktext from both and try again
		proj4str1 = self.__removeFromProj4(crs1.toProj4(), ['+towgs84', '+nadgrids', '+wktext'])
		proj4str2 = self.__removeFromProj4(crs2.toProj4(), ['+towgs84', '+nadgrids', '+wktext'])

		newcrs1 = QgsCoordinateReferenceSystem()
		newcrs2 = QgsCoordinateReferenceSystem()
		if newcrs1.createFromProj4( proj4str1 ) and newcrs1.isValid() and \
				newcrs2.createFromProj4( proj4str2 ) and newcrs2.isValid():
			if newcrs1 == newcrs2:
				return True

		return False

	def hasSameInputCrsBase(self, crs, isInverse=False):
		incrs = self.getInputCrs(isInverse)
		return self.sameBaseCrs(crs, incrs)

	def hasSameOutputCrsBase(self, crs, isInverse=False):
		outcrs = self.getOutputCrs(isInverse)
		return self.sameBaseCrs(crs, outcrs)


	def _getInputCrs(self):
		crs = QgsCoordinateReferenceSystem( self.inCrs )
		if not crs.isValid():
			if not crs.createFromProj4( self.inCrs ):
				qWarning( u"unable to create the input CRS from '%s'" % self.inCrs )
		return crs

	def _getOutputCrs(self):
		crs = QgsCoordinateReferenceSystem( self.outCrs )
		if not crs.isValid():
			if not crs.createFromProj4( self.outCrs ):
				qWarning( u"unable to create the output CRS from '%s'" % self.outCrs )
		return crs

	def getInputCrs(self, isInverse=False):
		return self._getInputCrs() if not isInverse else self._getOutputCrs()

	def getOutputCrs(self, isInverse=False):
		return self._getOutputCrs() if not isInverse else self._getInputCrs()


	def _getInputCustomCrs(self):
		crs = self._getInputCrs()
		proj4 = self.__removeFromProj4(crs.toProj4(), ['+nadgrids', '+towgs84', '+wktext'])
		if self.useGrid():
			proj4 = self.__addToProj4(proj4, {'+nadgrids':self.inGrid, '+wktext':None})
		elif self.useTowgs84():
			proj4 = self.__addToProj4(proj4, {'+towgs84':self.inTowgs84, '+wktext':None})
		crs.createFromProj4( proj4 )
		return crs

	def _getOutputCustomCrs(self):
		crs = self._getOutputCrs()
		if self.useGrid() or self.useTowgs84():
			proj4 = self.__removeFromProj4(crs.toProj4(), ['+nadgrids', '+towgs84', '+wktext'])
			if False and self.outTowgs84 != None:	# TODO self.outTowgs84 not supported yet
				# if a new +towgs84 param value was defined
				proj4 = self.__addToProj4(proj4, {'+towgs84':self.outTowgs84, '+wktext':None})
			else: 
				# use +nadgrids=null param
				proj4 = self.__addToProj4(proj4, {'+nadgrids':'null', '+wktext':None})

			crs.createFromProj4( proj4 )
		return crs


	def getInputCustomCrs(self, isInverse=False):
		return self._getInputCustomCrs() if not isInverse else self._getOutputCustomCrs()

	def getOutputCustomCrs(self, isInverse=False):
		return self._getOutputCustomCrs() if not isInverse else self._getInputCustomCrs()


	@classmethod
	def __existIntoProj4(self, proj4, param):
		return self.__valueIntoProj4(proj4, param) != None

	@classmethod
	def __valueIntoProj4(self, proj4, param):
		parts = self.__proj4StringToParts(proj4)
		if not parts.has_key( param ):
			return None	# param not found
		val = parts[ param ]
		return val if val != None else ""

	@classmethod
	def __addToProj4(self, proj4, params=None):
		if params == None:
			return proj4

		parts = self.__proj4StringToParts(proj4)
		for k, v in params.iteritems():
			parts[k] = v
		return self.__proj4PartsToString( parts )

	@classmethod
	def __removeFromProj4(self, proj4, params=None):
		if params == None:
			return proj4

		parts = self.__proj4StringToParts(proj4)
		for k in params:
			if parts.has_key(k):
				del parts[k]

		return self.__proj4PartsToString( parts )


	@classmethod
	def __proj4StringToParts(self, proj4string):
		parts = QString(proj4string).split( QRegExp( "\\s+(?=\\+[a-z][a-z_0-9]*)" ), QString.SkipEmptyParts )
		part_dict = {}
		for p in parts:
			regex = QRegExp( "^(\\+[a-z][a-z_0-9]*)(?:\\=(.+))?$" )
			if regex.indexIn( p ) < 0:
				continue

			if regex.pos(1) < 0:
				continue
			name = unicode(regex.cap(1))

			value = None
			if regex.pos(2) >= 0:
				value = unicode(regex.cap(2))

			part_dict[ name ] = value

		return part_dict

	@classmethod
	def __proj4PartsToString(self, proj4parts):
		parts = dict( proj4parts )

		# the proj4string must start with +proj=...
		if parts.has_key("+proj"):
			proj4 = u"+proj=%s" % parts["+proj"]
			del parts["+proj"]

		for k, v in parts.iteritems():
			proj4 += u" %s" % k if v == None else u" %s=%s" % (k,v)

		return proj4


	@classmethod
	def __valuesAreEqual(self, value1, value2):
		if value1 == value2:
			return True
		try:
			val1 = float(value1)
			val2 = float(value1)
		except ValueError:
			return False
		return abs(val1 - val2) < 0.000001


	### SECTION import/export from xml
	XML_TRANSF_DOC = "QGisTransformationTools"
	XML_TRANSF_LIST_TAG = "transformations"
	XML_TRANSF_TAG = "transformation"

	def _toNode(self, doc):
		node = doc.createElement( self.XML_TRANSF_TAG )
		for f in Transformation.fields:
			if f == "id":
				continue

			v = getattr(self, f, None)
			v = QString(v) if v != None else QString()

			if f in [ "name", "enabled" ]:
				node.setAttribute( f, v )
			else:
				child = doc.createElement( f )
				node.appendChild( child )
				t = doc.createTextNode( v )
				child.appendChild( t )

		return node

	def _fromNode(self, node):
		elem = node.toElement()
		if elem.tagName() != self.XML_TRANSF_TAG:
			return False

		# set props from attributes
		attrs = elem.attributes()
		for i in range( attrs.count() ):
			a = attrs.item( i ).toAttr()
			f = unicode( a.name() )
			if f == "id" or not f in Transformation.fields:
				continue

			v = a.value()
			setattr(self, f, v if not v.isEmpty() else None)

		# set props from nodes
		childNode = elem.firstChild()
		while not childNode.isNull():
			dataNode = childNode.toElement().firstChild()
			if not dataNode.isNull() and not dataNode.toText().isNull():
				f = unicode( childNode.toElement().tagName() )
				if f == "id" or not f in Transformation.fields:
					continue

				v = dataNode.toText().data()
				setattr(self, f, v if not v.isEmpty() else None)
			
			childNode = childNode.nextSibling()

		return True

	@classmethod
	def importFromXml(self, fn):
		f = QFile( fn )
		if not f.exists() or not f.open( QIODevice.ReadOnly ):
			QMessageBox.warning( None, "Importing", "File not found." )
			return False

		if f.size() <= 0 or f.atEnd():
			return False

		from PyQt4.QtXml import QDomDocument
		doc = QDomDocument( self.XML_TRANSF_DOC )
		(ok, errMsg, errLine, errCol) = doc.setContent( f, False )
		f.close()

		if not ok:
			QMessageBox.warning( None, "Importing", "Failed to parse file: line %s col %s" % (errLine, errCol) )
			return False

		root = doc.documentElement()
		if root.tagName() == self.XML_TRANSF_LIST_TAG:
			node = root.firstChild()
			while not node.isNull():
				if node.toElement().tagName() == self.XML_TRANSF_TAG:
					t = Transformation()
					if t._fromNode( node ):
						if t.inGrid != None:
							finfo = QFileInfo( t.inGrid )
							if not finfo.exists():
								t.inGrid = finfo.fileName()
						t.saveData()

				node = node.nextSibling()

		return True


	@classmethod
	def exportToXml(self, fn):
		from PyQt4.QtXml import QDomDocument
		doc = QDomDocument( self.XML_TRANSF_DOC )

		instr = doc.createProcessingInstruction("xml","version=\"1.0\" encoding=\"UTF-8\" ")
		doc.appendChild(instr)

		root = doc.createElement( self.XML_TRANSF_LIST_TAG )
		doc.appendChild( root )

		for t in Transformation.getAll():
			root.appendChild( t._toNode( doc ) )

		f = QFile( fn )
		if not f.open( QIODevice.WriteOnly ):
			return False

		xmlStream = QTextStream( f )
		xmlStream.setCodec( QTextCodec.codecForName( "UTF-8" ) )
		xmlStream << doc.toString()
		return True



def initializedb():
	""" create the table on qgis.db if not exists yet
	 paying attention to db changes between different versions """

	dropNow = False
	vers_with_db_changes = ['', '0.0.3']

	settings = QSettings()
	#settings.setValue("/Transformation_Tools/last_version", "")

	last_version = settings.value("/TransformationTools/last_version", "").toString()
	import TransformationTools
	new_version = TransformationTools.version()
	if last_version != new_version:
		settings.setValue("/TransformationTools/last_version", new_version)
		if last_version in vers_with_db_changes:
			dropNow = True

	Transformation.createTable(dropNow)

initializedb()
