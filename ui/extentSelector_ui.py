# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/extentSelector.ui'
#
# Created: Tue Apr 19 19:39:10 2011
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ExtentSelector(object):
    def setupUi(self, ExtentSelector):
        ExtentSelector.setObjectName("ExtentSelector")
        ExtentSelector.resize(343, 134)
        self.gridLayout = QtGui.QGridLayout(ExtentSelector)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(ExtentSelector)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_7 = QtGui.QLabel(ExtentSelector)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 3, 0, 1, 2)
        self.widget = QtGui.QWidget(ExtentSelector)
        self.widget.setObjectName("widget")
        self.gridLayout_3 = QtGui.QGridLayout(self.widget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_11 = QtGui.QLabel(self.widget)
        self.label_11.setObjectName("label_11")
        self.gridLayout_3.addWidget(self.label_11, 0, 2, 1, 1)
        self.x1CoordEdit = QtGui.QLineEdit(self.widget)
        self.x1CoordEdit.setObjectName("x1CoordEdit")
        self.gridLayout_3.addWidget(self.x1CoordEdit, 0, 3, 1, 1)
        self.label_13 = QtGui.QLabel(self.widget)
        self.label_13.setObjectName("label_13")
        self.gridLayout_3.addWidget(self.label_13, 0, 7, 1, 1)
        self.x2CoordEdit = QtGui.QLineEdit(self.widget)
        self.x2CoordEdit.setObjectName("x2CoordEdit")
        self.gridLayout_3.addWidget(self.x2CoordEdit, 0, 8, 1, 1)
        self.y1CoordEdit = QtGui.QLineEdit(self.widget)
        self.y1CoordEdit.setObjectName("y1CoordEdit")
        self.gridLayout_3.addWidget(self.y1CoordEdit, 1, 3, 1, 1)
        self.y2CoordEdit = QtGui.QLineEdit(self.widget)
        self.y2CoordEdit.setObjectName("y2CoordEdit")
        self.gridLayout_3.addWidget(self.y2CoordEdit, 1, 8, 1, 1)
        self.label_15 = QtGui.QLabel(self.widget)
        self.label_15.setObjectName("label_15")
        self.gridLayout_3.addWidget(self.label_15, 1, 7, 1, 1)
        self.label_14 = QtGui.QLabel(self.widget)
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 1, 2, 1, 1)
        self.label_12 = QtGui.QLabel(self.widget)
        self.label_12.setIndent(20)
        self.label_12.setObjectName("label_12")
        self.gridLayout_3.addWidget(self.label_12, 0, 6, 2, 1)
        self.label_10 = QtGui.QLabel(self.widget)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 0, 1, 2, 1)
        self.gridLayout.addWidget(self.widget, 4, 0, 1, 2)
        self.btnEnable = QtGui.QPushButton(ExtentSelector)
        self.btnEnable.setObjectName("btnEnable")
        self.gridLayout.addWidget(self.btnEnable, 1, 1, 1, 1)

        self.retranslateUi(ExtentSelector)
        QtCore.QMetaObject.connectSlotsByName(ExtentSelector)

    def retranslateUi(self, ExtentSelector):
        self.label.setText(QtGui.QApplication.translate("ExtentSelector", "Select the extent by drag on canvas", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("ExtentSelector", "or change the extent coordinates", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("ExtentSelector", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("ExtentSelector", "x", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("ExtentSelector", "y", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("ExtentSelector", "y", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("ExtentSelector", "2", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("ExtentSelector", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEnable.setText(QtGui.QApplication.translate("ExtentSelector", "Re-Enable", None, QtGui.QApplication.UnicodeUTF8))

