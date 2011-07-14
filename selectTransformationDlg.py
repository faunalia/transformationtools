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

from transformationsTableModel import FilteredTransformationsTableModel
from ui.selectTransformation_ui import Ui_Dialog

import resources_rc

class SelectTransformationDlg(QDialog, Ui_Dialog):

	APPLY_WITHOUT_ASK = []
	
	def __init__(self, layerName, layerCrs, mapCrs, parent=None):
		QDialog.__init__(self, parent)
		self.setupUi(self)
		self.layerNameLbl.setText( layerName )
		self.layerCrsLbl.setText( layerCrs.authid() )
		self.layerCrsLbl.setToolTip( layerCrs.toProj4() )
		self.layerCrsToolTip.setPixmap( QPixmap(':/plugins/TransformationTools/icons/tooltip.png') )
		self.layerCrsToolTip.setToolTip( layerCrs.toProj4() )

		# if only one transformation, use it without ask for confirmation
		self.useIfOne = False

		self.table.setModel( FilteredTransformationsTableModel(layerCrs, mapCrs, self, True, False) )
		self.table.setTextElideMode( Qt.ElideMiddle )

		self.connect(self.table.selectionModel(), SIGNAL("selectionChanged(const QItemSelection&, const QItemSelection&)"), self.itemChanged)
		self.connect(self.table, SIGNAL("doubleClicked(const QModelIndex&)"), self.accept)
		self.itemChanged()

	def exec_(self, forceDialog=False):
		if self.table.model().rowCount() <= 0:
			return False

		if not forceDialog:
			if self.useIfOne and self.table.model().rowCount() == 1:
				self.table.selectRow( 0 )
				return True

			if self.applyAutomatically():
				return True

		return QDialog.exec_(self)

	def applyAutomatically(self):
		for row in range(self.table.model().rowCount()):
			t = self.table.model().getAtRow( row )
			if not t in SelectTransformationDlg.APPLY_WITHOUT_ASK:
				continue
			self.table.selectRow( row )
			return True
		return False

	def getSelected(self):
		index = self.table.currentIndex()
		if not index.isValid():
			return
		return self.table.model().getAtRow( index.row() )

	def getCrss(self):
		t, isInverse = self.getSelected()
		return t.getInputCustomCrs( isInverse ), t.getOutputCustomCrs( isInverse )

	def itemChanged(self):
		rows = self.table.selectionModel().selectedRows()
		if len(rows) > 0:
			self.table.setCurrentIndex( rows[0] )
		elif self.table.model().rowCount() > 0:
			self.table.selectRow( 0 )

	def accept(self):
		t = self.getSelected()
		if t == None:
			# shouldn't happen because the first row is selected when the dialog is displayed
			QMessageBox.information(self, self.tr(u"Sorry"), self.tr(u"Nothing selected"))
			return False

		if self.applyToNext.isChecked():
			SelectTransformationDlg.APPLY_WITHOUT_ASK.insert( 0, t )

		return QDialog.accept(self)

