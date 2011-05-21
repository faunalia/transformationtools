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

from ui.editTransformation_ui import Ui_Dialog
from transformations import Transformation

class EditTransformationDlg(QDialog, Ui_Dialog):
	
	def __init__(self, transformation, parent=None):
		QDialog.__init__(self, parent)
		self.transformation = transformation
		self.setupUi(self)
		if self.parent() != None:
			self.extentSelector.setCanvas( self.parent().iface.mapCanvas() )

		self.extentGroup.hide()

		self.connect(self.selectGridBtn, SIGNAL("clicked()"), self.selectPathToGrids)
		self.connect(self.selectInputCrsBtn, SIGNAL("clicked()"), self.selectInputCrs)
		self.connect(self.selectOutputCrsBtn, SIGNAL("clicked()"), self.selectOutputCrs)
		self.connect(self.extentGroup, SIGNAL("toggled(bool)"), self.onExtentCheckedChanged)

		self.reset()

	def selectInputCrs(self):
		from selectCrsDlg import SelectCrsDlg
		dlg = SelectCrsDlg( "Select the input CRS", self )
		if dlg.exec_():
			self.inputCrsEdit.setText(dlg.getProjection())

	def selectOutputCrs(self):
		from selectCrsDlg import SelectCrsDlg
		dlg = SelectCrsDlg( "Select the output CRS", self )
		if dlg.exec_():
			self.outputCrsEdit.setText(dlg.getProjection())

	def onExtentCheckedChanged(self, enabled):
		self.setModal( not enabled )
		if self.parent() != None:
			self.parent().setVisible( not enabled )
		self.update()
		self.extentSelector.start() if enabled else self.extentSelector.stop()


	def reset(self):
		self.fillGridCombo()
		self.extentGroup.setChecked( False )

		fix_string = lambda x: QString(x) if x != None else QString()
		self.nameEdit.setText( fix_string(self.transformation.name) )
		self.inputCrsEdit.setText( fix_string(self.transformation.incrs) )
		self.outputCrsEdit.setText( fix_string(self.transformation.outcrs) )

		if self.transformation.towgs84 != None:
			self.towgs84Radio.setChecked(True)
			self.towgs84Edit.setText( fix_string(self.transformation.towgs84) )
		else:
			self.gridRadio.setChecked(True)
			grid = fix_string(self.transformation.grid)
			index = self.gridCombo.findData( grid )
			if index < 0 and grid.isEmpty() and self.gridCombo.count() > 0:
				index = 0
			self.gridCombo.setCurrentIndex( index )
			if self.gridCombo.currentIndex() < 0:
				self.gridCombo.setEditText( grid )

		self.extentGroup.setChecked( self.transformation.extent != None )
		self.extentSelector.setExtent( self.transformation.extent )
		
		self.inputCustomCrsNameEdit.setText( fix_string(self.transformation.newincrsname) )
		self.outputCustomCrsNameEdit.setText( fix_string(self.transformation.newoutcrsname) )

	def getPathToGrids(self):
		settings = QSettings()
		return settings.value( u"/transformations/pathToGrids", "" ).toString()

	def setPathToGrids(self, path):
		settings = QSettings()
		settings.setValue( u"/transformations/pathToGrids", path if path != None else "" )

	def selectPathToGrids(self):
		path = self.getPathToGrids()
		inDir = QFileDialog.getExistingDirectory(self, self.tr( "Select the directory with grids" ), path)
		if inDir.isEmpty():
			return
		settings = QSettings()
		self.setPathToGrids( inDir )
		self.fillGridCombo()

	def fillGridCombo(self):
		path = self.getPathToGrids()
		gridDir = QDir( path )
		gridDir.setFilter( QDir.Files | QDir.NoSymLinks | QDir.NoDotAndDotDot )
		gridDir.setNameFilters( QStringList() << "*.gsb" )

		self.gridCombo.clear()		
		for g in gridDir.entryList():
			fn = u"%s/%s" % (path, g)
			self.gridCombo.addItem( g, fn )

	def accept(self):
		invalid = self.nameEdit.text().isEmpty()
		invalid = invalid or ( self.inputCrsEdit.text().isEmpty() or self.outputCrsEdit.text().isEmpty() )
		invalid = invalid or ( self.gridRadio.isChecked() and self.gridCombo.currentIndex() < 0 and self.gridCombo.currentText().isEmpty() )
		invalid = invalid or ( self.towgs84Radio.isChecked() and self.towgs84Edit.text().isEmpty() )
		invalid = invalid or ( self.inputCustomCrsNameEdit.text().isEmpty() or self.outputCustomCrsNameEdit.text().isEmpty() )
		if invalid:
			QMessageBox.warning(self, self.tr(u"Some required field is empty"), self.tr(u"You must fill all fields to continue.") )
			return

		# don't overwrite different transformation with the same name
		#if self.nameEdit.text() != self.transformation.name and Transformation.exists( self.nameEdit.text() ):
		#	QMessageBox.warning(self, self.tr(u"Name exists"), self.tr(u"%s exists yet, use a different transformation name." % self.nameEdit.text()) )
		#	return

		self.transformation.name = self.nameEdit.text()

		if self.gridRadio.isChecked():
			index = self.gridCombo.currentIndex()
			text = self.gridCombo.currentText()
			if index < 0 or text != self.gridCombo.itemText( index ):
				self.transformation.grid = text
			else:
				self.transformation.grid = self.gridCombo.itemData( index ).toString()
		else:
			self.transformation.grid = None

		self.transformation.towgs84 = self.towgs84Edit.text() if self.towgs84Radio.isChecked() else None
		self.transformation.extent = self.extentSelector.getExtent() if self.extentGroup.isChecked() else None

		self.transformation.incrs = self.inputCrsEdit.text()
		self.transformation.outcrs = self.outputCrsEdit.text()
		self.transformation.newincrsname = self.inputCustomCrsNameEdit.text()
		self.transformation.newoutcrsname = self.outputCustomCrsNameEdit.text()

		self.onClosing()
		return QDialog.accept(self)

	def reject(self):
		self.onClosing()
		return QDialog.reject(self)

	def onClosing(self):
		self.extentSelector.stop()

