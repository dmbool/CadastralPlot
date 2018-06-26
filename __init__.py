# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CadastralPlot
                                 A QGIS plugin
 Plot cadastral data
                             -------------------
        begin                : 2018-02-27
        copyright            : (C) 2018 by dmbool
        email                : dmbool@up.edu.ph
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CadastralPlot class from file CadastralPlot.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .CadastralPlot import CadastralPlot
    return CadastralPlot(iface)
