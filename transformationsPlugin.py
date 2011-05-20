# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : Transformations
Description          : Allow to use grids and towgs84 to transform a vector/raster
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

from qgis.core import *
from qgis.gui import *

#import resources

class TransformationsPlugin:

	def __init__(self, iface):
		# Save a reference to the QGIS iface
		self.iface = iface
		
	def initGui(self):
		self.managerAction = QAction(QIcon(), "Transformation Manager", self.iface.mainWindow())
		QObject.connect(self.managerAction, SIGNAL("triggered()"), self.runManager)

		self.transformAction = QAction(QIcon(), "Transform", self.iface.mainWindow())
		QObject.connect(self.transformAction, SIGNAL("triggered()"), self.runTransform)

		self.aboutAction = QAction("About", self.iface.mainWindow())
		QObject.connect(self.aboutAction, SIGNAL("triggered()"), self.about)


		# Add to the plugin menu and toolbar
		self.iface.addPluginToMenu("Transformation Manager", self.managerAction)
		#self.iface.addPluginToMenu("Transformation Manager", self.transformAction)
		self.iface.addPluginToMenu("Transformation Manager", self.aboutAction)
		self.iface.addToolBarIcon(self.transformAction)
		self.iface.addToolBarIcon(self.managerAction)

		QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWasAdded(QgsMapLayer *)"), self.setTransformation)

	def unload(self):
		QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL("layerWasAdded(QgsMapLayer *)"), self.setTransformation)

		# Remove the plugin
		self.iface.removePluginMenu("Transformation Manager", self.managerAction)
		#self.iface.removePluginMenu("Transformation Manager", self.transformAction)
		self.iface.removePluginMenu("Transformation Manager", self.aboutAction)
		self.iface.removeToolBarIcon(self.transformAction)
		self.iface.removeToolBarIcon(self.managerAction)

	def about(self):
		from dlgAbout import DlgAbout
		DlgAbout(self.iface.mainWindow()).exec_()


	def runManager(self):
		from transformationManagerDlg import TransformationManagerDlg
		dlg = TransformationManagerDlg(self.iface, self.iface.mainWindow())
		dlg.exec_()

	def runTransform(self):
		pass

	def setTransformation(self, layer):
		prevRender = self.iface.mapCanvas().renderFlag()
		try:
			self.iface.mapCanvas().setRenderFlag(False)
			from selectTransformationDlg import SelectTransformationDlg
			dlg = SelectTransformationDlg(self.iface, layer, self.iface.mainWindow())
			dlg.exec_()
		finally:
			self.iface.mapCanvas().setRenderFlag(prevRender)

