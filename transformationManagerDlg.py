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

from transformationsTableModel import TransformationsTableModel
from ui.transformationManager_ui import Ui_Dialog
from transformations import Transformation

class TransformationManagerDlg(QDialog, Ui_Dialog):
	
	def __init__(self, iface, parent=None):
		QDialog.__init__(self, parent)
		#self.setWindowFlags( Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint & ~Qt.WindowMinimizeButtonHint )
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.iface = iface
		self.setupUi(self)

		self.table.setModel( TransformationsTableModel(self) )
		self.table.setTextElideMode( Qt.ElideMiddle )

		self.connect(self.table.selectionModel(), SIGNAL("selectionChanged(const QItemSelection&, const QItemSelection&)"), self.itemChanged)
		self.connect(self.table, SIGNAL("doubleClicked(const QModelIndex&)"), self.editItem)

		self.connect(self.newBtn, SIGNAL("clicked()"), self.createNew)
		self.connect(self.editBtn, SIGNAL("clicked()"), self.editItem)
		self.connect(self.deleteBtn, SIGNAL("clicked()"), self.deleteItem)
		self.connect(self.applyDirectBtn, SIGNAL("clicked()"), self.applyDirectTransf)
		self.connect(self.applyInverseBtn, SIGNAL("clicked()"), self.applyInverseTransf)

		self.connect(self.importBtn, SIGNAL("clicked()"), self.importFromFile)
		self.connect(self.exportBtn, SIGNAL("clicked()"), self.exportToFile)

		self.itemChanged()

	def createNew(self):
		self.editTransformation( Transformation() )

	def editTransformation(self, t):
		from editTransformationDlg import EditTransformationDlg
		dlg = EditTransformationDlg( t, self )
		if dlg.exec_():
			t.saveData()
		self.refreshTable()

	def editItem(self, index=None):
		if index == None:
			index = self.table.currentIndex()
		if not index.isValid():
			return
		t = self.table.model().getAtRow( index.row() )
		self.editTransformation( t )

	def deleteItem(self, index=None):
		if index == None:
			index = self.table.currentIndex()
		if not index.isValid():
			return
		t = self.table.model().getAtRow( index.row() )
		res = QMessageBox.question(self, self.tr(u"Delete transformation"), self.tr(u"Really delete transformation '%1'?" ).arg(t.name), QMessageBox.Yes | QMessageBox.No)
		if res == QMessageBox.No:
			return

		t.deleteData()
		self.refreshTable()


	def applyDirectTransf(self):
		self.applyTransformation(False)

	def applyInverseTransf(self):
		self.applyTransformation(True)

	def applyTransformation(self, isInverse=False, index=None):
		if index == None:
			index = self.table.currentIndex()
		if not index.isValid():
			return
		t = self.table.model().getAtRow( index.row() )

		canvas = self.iface.mapCanvas()
		prevRender = canvas.renderFlag()
		try:
			canvas.setRenderFlag(False)
			mapRenderer = canvas.mapRenderer()
			mapCrs = (mapRenderer.destinationCrs if hasattr(mapRenderer, 'destinationCrs') else mapRenderer.destinationSrs)()
			(mapRenderer.setDestinationCrs if hasattr(mapRenderer, 'setDestinationCrs') else mapRenderer.setDestinationSrs)( t.getOutputCustomCrs(isInverse) )

			for layer in self.iface.legendInterface().layers():
				layerCrs = (layer.crs if hasattr(layer, 'crs') else layer.srs)()
				# layer CRS and project CRS match the transformation CRSs
				if t.isApplicableTo(layerCrs, mapCrs):
					layer.setCrs( t.getInputCustomCrs(isInverse) )
				elif t._sameBaseOutputCrs(layerCrs):
					# the layer CRS is pretty the same of the new project CRS, 
					# use the new project CRS
					layer.setCrs( t.getOutputCustomCrs(isInverse) )

			canvas.mapRenderer().setProjectionsEnabled( True )
		finally:
			canvas.setRenderFlag(prevRender)


	def itemChanged(self):
		rows = self.table.selectionModel().selectedRows()
		enable = len(rows) > 0
		if enable:
			self.table.setCurrentIndex( rows[0] )
		self.editBtn.setEnabled( enable )
		self.deleteBtn.setEnabled( enable )
		self.applyDirectBtn.setEnabled( enable )
		self.applyInverseBtn.setEnabled( enable )

	def refreshTable(self):
		self.table.model().reloadData()
		self.table.model().reset()
		self.itemChanged()


	### SECTION import/export transformations

	def exportToFile(self):
		outfile = QFileDialog.getSaveFileName(self, self.tr( "Select where to export transformations" ), self.lastImportFile(), self.tr( "XML file (*.xml)" ))
		if outfile.isEmpty():
			return
		if not outfile.endsWith( ".xml", Qt.CaseInsensitive ):
			outfile += ".xml"
		self.setLastImportFile( outfile )

		return Transformation.exportToXml( outfile )

	def importFromFile(self):
		tlist = Transformation.getAll()
		if len( tlist ) > 0:
			ret = QMessageBox.question(self, self.tr( "Import" ), self.tr( "Do you want to keep the defined transformations?" ), QMessageBox.Yes | QMessageBox.No )

		infile = QFileDialog.getOpenFileName(self, self.tr( "Select the file containing transformations" ), self.lastImportFile(), self.tr( "XML file (*.xml)" ))
		if infile.isEmpty():
			return
		self.setLastImportFile( infile )

		if len( tlist ) > 0 and ret == QMessageBox.No:
			# clear all existent transformations before continue
			for t in tlist:
				t.deleteData()

		if not Transformation.importFromXml( infile ):
			return False

		self.table.model().reloadData()
		self.table.model().reset()
		return True
		

	def lastImportFile(self):
		settings = QSettings()
		return settings.value( u"/TransformationTools/lastImportFile", "" ).toString()

	def setLastImportFile(self, path):
		settings = QSettings()
		settings.setValue( u"/TransformationTools/lastImportFile", path if path != None else "" )

