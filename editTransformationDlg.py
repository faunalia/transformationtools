from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui.editTransformation_ui import Ui_Dialog
from transformation import Transformation

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
		self.inputCrsEdit.setText( fix_string(self.transformation.inCrs) )
		self.outputCrsEdit.setText( fix_string(self.transformation.outCrs) )

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
		
		self.inputCustomCrsNameEdit.setText( fix_string(self.transformation.inCustomCrsName) )
		self.outputCustomCrsNameEdit.setText( fix_string(self.transformation.outCustomCrsName) )

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

		if self.nameEdit.text() != self.transformation.name:
			# don't overwrite different transformation with the same name
			if Transformation.exists( self.nameEdit.text() ):
				QMessageBox.warning(self, self.tr(u"Name exists"), self.tr(u"%s exists yet, use a different transformation name." % self.nameEdit.text()) )
				return

		grid = None
		if self.gridRadio.isChecked():
			index = self.gridCombo.currentIndex()
			text = self.gridCombo.currentText()
			if index < 0 or text != self.gridCombo.itemText( index ):
				grid = text
			else:
				grid = self.gridCombo.itemData( index )

		towgs84 = None
		if self.towgs84Radio.isChecked():
			towgs84 = self.towgs84Edit.text()

		extent = None
		if self.extentGroup.isChecked():
			extent = self.extentSelector.getExtent()

		params = [self.nameEdit.text(), self.inputCrsEdit.text(), self.outputCrsEdit.text(), 
				grid, towgs84, extent, self.inputCustomCrsNameEdit.text(), self.outputCustomCrsNameEdit.text(), 
				self.transformation.enabled]
		self.transformation.setPropValues( params )

		self.onClosing()
		return QDialog.accept(self)

	def reject(self):
		self.onClosing()
		return QDialog.reject(self)

	def onClosing(self):
		self.extentSelector.stop()

