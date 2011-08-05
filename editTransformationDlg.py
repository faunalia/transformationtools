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

		to_string = lambda x: QString(x) if x != None else QString()
		self.nameEdit.setText( to_string(self.transformation.name) )
		self.inputCrsEdit.setText( to_string(self.transformation.inCrs) )
		self.outputCrsEdit.setText( to_string(self.transformation.outCrs) )

		if self.transformation.inTowgs84 != None:
			self.inTowgs84Radio.setChecked(True)
			self.inTowgs84Edit.setText( to_string(self.transformation.inTowgs84) )
		else:
			self.inGridRadio.setChecked(True)
			grid = to_string(self.transformation.inGrid)
			index = self.inGridCombo.findData( grid )
			if index < 0 and grid.isEmpty() and self.inGridCombo.count() > 0:
				index = 0
			self.inGridCombo.setCurrentIndex( index )
			if self.inGridCombo.currentIndex() < 0:
				self.inGridCombo.setEditText( grid ) 
		self.outTowgs84Edit.setText( to_string(self.transformation.outTowgs84) )

		self.extentGroup.setChecked( self.transformation.extent != None )
		self.extentSelector.setExtent( self.transformation.extent )

		if self.transformation.id != None:
			newincrsname = to_string(self.transformation.newInCrsName)
			if newincrsname != "":
				self.inputCustomCrsNameEdit.setText( newincrsname )
			else:
				self.inputCustomCrsNameEdit.setText( self.transformation.getInputCustomCrs().authid() )

			newoutcrsname = to_string(self.transformation.newOutCrsName)
			if newoutcrsname != "":
				self.outputCustomCrsNameEdit.setText( newoutcrsname )
			else:
				self.outputCustomCrsNameEdit.setText( self.transformation.getOutputCustomCrs().authid() )


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

		self.inGridCombo.clear()		
		for g in gridDir.entryList():
			fn = u"%s/%s" % (path, g)
			self.inGridCombo.addItem( g, fn )

	def accept(self):
		invalid = self.nameEdit.text().isEmpty()
		invalid = invalid or ( self.inputCrsEdit.text().isEmpty() or self.outputCrsEdit.text().isEmpty() )
		invalid = invalid or ( self.inGridRadio.isChecked() and self.inGridCombo.currentIndex() < 0 and self.inGridCombo.currentText().isEmpty() )
		invalid = invalid or ( self.inTowgs84Radio.isChecked() and self.inTowgs84Edit.text().isEmpty() )
		if invalid:
			QMessageBox.warning(self, self.tr(u"Some required field is empty"), self.tr(u"You must fill all fields to continue.") )
			return

		# don't overwrite different transformation with the same name
		#if self.nameEdit.text() != self.transformation.name and Transformation.exists( self.nameEdit.text() ):
		#	QMessageBox.warning(self, self.tr(u"Name exists"), self.tr(u"%s exists yet, use a different transformation name." % self.nameEdit.text()) )
		#	return

		self.transformation.name = self.nameEdit.text()

		self.transformation.inCrs = self.inputCrsEdit.text()
		self.transformation.outCrs = self.outputCrsEdit.text()

		if self.inGridRadio.isChecked():
			index = self.inGridCombo.currentIndex()
			text = self.inGridCombo.currentText()
			if index < 0 or text != self.inGridCombo.itemText( index ):
				self.transformation.inGrid = text
			else:
				self.transformation.inGrid = self.inGridCombo.itemData( index ).toString()
		else:
			self.transformation.inGrid = None

		self.transformation.inTowgs84 = self.inTowgs84Edit.text() if self.inTowgs84Radio.isChecked() else None
		self.transformation.extent = self.extentSelector.getExtent() if self.extentGroup.isChecked() else None
		self.transformation.outTowgs84 = self.outTowgs84Edit.text() if not self.outTowgs84Edit.text().isEmpty() else None

		incrsname = self.inputCustomCrsNameEdit.text()
		self.transformation.newInCrsName = incrsname if self.inputCustomCrsNameEdit.isEnabled() and not incrsname.isEmpty() else None
		outcrsname = self.outputCustomCrsNameEdit.text()
		self.transformation.newOutCrsName = outcrsname if self.outputCustomCrsNameEdit.isEnabled() and not outcrsname.isEmpty() else None

		self.onClosing()
		return QDialog.accept(self)

	def reject(self):
		self.onClosing()
		return QDialog.reject(self)

	def onClosing(self):
		self.extentSelector.stop()

