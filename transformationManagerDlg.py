from PyQt4.QtCore import *
from PyQt4.QtGui import *

from transformationsTableModel import TransformationsTableModel
from ui.transformationManager_ui import Ui_Dialog

class TransformationManagerDlg(QDialog, Ui_Dialog):
	
	def __init__(self, iface, parent=None):
		QDialog.__init__(self, parent)
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
		t.deleteData()
		self.refreshTable()

	def itemChanged(self):
		rows = self.table.selectionModel().selectedRows()
		enable = len(rows) > 0
		if enable:
			self.table.setCurrentIndex( rows[0] )
		self.editBtn.setEnabled( enable )
		self.deleteBtn.setEnabled( enable )

	def refreshTable(self):
		self.table.model().reloadData()
		self.table.model().reset()
		self.itemChanged()

