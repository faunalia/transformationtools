from PyQt4.QtCore import *
from PyQt4.QtGui import *

from transformationsTableModel import FilteredTransformationsTableModel
from ui.selectTransformation_ui import Ui_Dialog

class SelectTransformationDlg(QDialog, Ui_Dialog):
	
	def __init__(self, iface, layer, parent=None):
		QDialog.__init__(self, parent)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.iface = iface
		self.layer = layer
		self.setupUi(self)

		# if only one transformation, use it without ask for confirmation
		self.useIfOne = True

		inCrs = self.layer.crs()
		outCrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
		self.table.setModel( FilteredTransformationsTableModel(inCrs, outCrs, self, True, False) )
		self.table.setTextElideMode( Qt.ElideMiddle )

		self.connect(self.table.selectionModel(), SIGNAL("selectionChanged(const QItemSelection&, const QItemSelection&)"), self.itemChanged)
		self.connect(self.table, SIGNAL("doubleClicked(const QModelIndex&)"), self.accept)
		self.itemChanged()

	def exec_(self):
		if self.table.model().rowCount() <= 0:
			return False
		if self.useIfOne and self.table.model().rowCount() == 1:
			self.setLayerCrs(0)
			return True
		return QDialog.exec_(self)

	def setLayerCrs(self, row=None):
		if row == None:
			index = self.table.currentIndex()
			if not index.isValid():
				return False
			row = index.row()

		t = self.table.model().getAtRow( row )
		self.iface.mapCanvas().mapRenderer().setDestinationCrs( t.getOutputCustomCrs() )
		self.layer.setCrs( t.getInputCustomCrs() )
		return True

	def itemChanged(self):
		rows = self.table.selectionModel().selectedRows()
		if len(rows) > 0:
			self.table.setCurrentIndex( rows[0] )
		elif self.table.model().rowCount() > 0:
			self.table.selectRow( 0 )

	def accept(self):
		self.setLayerCrs()
		return QDialog.accept(self)

