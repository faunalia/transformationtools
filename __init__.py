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

def name():
	return "Transformation Tools"

def description():
	return "Help to use grids and towgs84 to transform a vector/raster"

def version():
	return "0.0.1"

def qgisMinimumVersion():
	return "1.6.0"

def authorName():
	return "Giuseppe Sucameli (Faunalia)"

def classFactory(iface):
	from transformationsPlugin import TransformationsPlugin
	return TransformationsPlugin(iface)

