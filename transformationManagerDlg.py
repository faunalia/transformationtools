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
		self.connect(self.applyBtn, SIGNAL("clicked()"), self.applyTransformation)
		self.itemChanged()

	def createNew(self):
		from transformations import Transformation
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

	def applyTransformation(self, index=None):
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

			from selectTransformationDlg import SelectTransformationDlg
			from .transformations import Transformation

			# show the dialog if the current transformation can be applyied to a loaded layer
			for layer in self.iface.legendInterface().layers():
				layerCrs = (layer.crs if hasattr(layer, 'crs') else layer.srs)()
				# get valid transformations for the layer 
				valid = False
				if t.isApplicableTo(layerCrs, mapCrs) or t.isApplicableTo(mapCrs,layerCrs):
					dlg = SelectTransformationDlg(layer.name(), layerCrs, mapCrs, self.iface.mainWindow())
					if dlg.exec_():
						layerCrs, mapCrs = dlg.getCrss()
						(mapRenderer.setDestinationCrs if hasattr(mapRenderer, 'setDestinationCrs') else mapRenderer.setDestinationSrs)( mapCrs )
						layer.setCrs( layerCrs )
					dlg.deleteLater()
					del dlg
		finally:
			canvas.setRenderFlag(prevRender)


	def itemChanged(self):
		rows = self.table.selectionModel().selectedRows()
		enable = len(rows) > 0
		if enable:
			self.table.setCurrentIndex( rows[0] )
		self.editBtn.setEnabled( enable )
		self.deleteBtn.setEnabled( enable )
		self.applyBtn.setEnabled( enable )

	def refreshTable(self):
		self.table.model().reloadData()
		self.table.model().reset()
		self.itemChanged()

