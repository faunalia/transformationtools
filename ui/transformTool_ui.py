# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/transformTool.ui'
#
# Created: Sat Apr 16 14:18:37 2011
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 174)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.vectorRadio = QtGui.QRadioButton(Dialog)
        self.vectorRadio.setChecked(True)
        self.vectorRadio.setObjectName("vectorRadio")
        self.gridLayout.addWidget(self.vectorRadio, 0, 1, 1, 1)
        self.rasterRadio = QtGui.QRadioButton(Dialog)
        self.rasterRadio.setObjectName("rasterRadio")
        self.gridLayout.addWidget(self.rasterRadio, 0, 2, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.inputEdit = QtGui.QLineEdit(Dialog)
        self.inputEdit.setObjectName("inputEdit")
        self.gridLayout.addWidget(self.inputEdit, 1, 1, 1, 3)
        self.selectInputBtn = QtGui.QToolButton(Dialog)
        self.selectInputBtn.setObjectName("selectInputBtn")
        self.gridLayout.addWidget(self.selectInputBtn, 1, 4, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.outputEdit = QtGui.QLineEdit(Dialog)
        self.outputEdit.setObjectName("outputEdit")
        self.gridLayout.addWidget(self.outputEdit, 2, 1, 1, 3)
        self.selectOutputBtn = QtGui.QToolButton(Dialog)
        self.selectOutputBtn.setObjectName("selectOutputBtn")
        self.gridLayout.addWidget(self.selectOutputBtn, 2, 4, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(Dialog)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 3, 1, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 5)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Run Transformation", None, QtGui.QApplication.UnicodeUTF8))
        self.vectorRadio.setText(QtGui.QApplication.translate("Dialog", "Vector", None, QtGui.QApplication.UnicodeUTF8))
        self.rasterRadio.setText(QtGui.QApplication.translate("Dialog", "Raster", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Input file", None, QtGui.QApplication.UnicodeUTF8))
        self.selectInputBtn.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Output file", None, QtGui.QApplication.UnicodeUTF8))
        self.selectOutputBtn.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Transformation", None, QtGui.QApplication.UnicodeUTF8))

