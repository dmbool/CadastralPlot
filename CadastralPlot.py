# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CadastralPlot
                                 A QGIS plugin
 Plot cadastral data
                              -------------------
        begin                : 2018-02-27
        git sha              : $Format:%H$
        copyright            : (C) 2018 by dmbool
        email                : dmbool@up.edu.ph
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from CadastralPlot_dialog import CadastralPlotDialog
import os.path, numpy as np, math as ma, re


class CadastralPlot:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CadastralPlot_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dlg = CadastralPlotDialog()
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Cadastral Plot')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'CadastralPlot')
        self.toolbar.setObjectName(u'CadastralPlot')
        
        self.dlg.lineSelect.clear()
        self.dlg.pushSelect.clicked.connect(self.select_InputFile)
#         
        self.dlg.lineOutput.clear()
        self.dlg.pushOutput.clicked.connect(self.select_OutputFile)
        
        self.dlg.radioTD.setChecked(True)
        self.dlg.radioC.setChecked(False)
        
        self.dlg.radioTD.toggled.connect(self.getFromTD)
        self.dlg.radioC.toggled.connect(self.getFromC)
        
        self.dlg.tableShow.setRowCount(0)
        
#         
#         self.dlg.comboBox.clear()
#         self.dlg.comboBox.clicked.connect(self.getCoordinates)
#         
#         self.dlg.comboBox2.clear()
#         self.dlg.comboBox2.clicked.connect(self.getBase)
        
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CadastralPlot', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference


        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/CadastralPlot/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Cadastral Plot'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&Cadastral Plot'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
 
    def getFromTD(self):
        if self.dlg.radioTD.isChecked():
            self.dlg.radioC.setChecked(False)
        else:
            self.dlg.radioC.setChecked(True)
    
    def getFromC(self):
        if self.dlg.radioC.isChecked():
            self.dlg.radioTD.setChecked(False)
        else:
            self.dlg.radioTD.setChecked(True)
            
    def closeEvent(self,event):
        self.reset_form()
         
    def select_InputFile(self):
        inputFileName = QFileDialog.getOpenFileName(self.dlg,"Select Input File ",r"C:\Deane\Data","*.txt")
        self.dlg.lineSelect.setText(inputFileName)
        select_file = open(self.dlg.lineSelect.text())
        self.dlg.tableShow.setRowCount(0)
        lines1 = select_file.readlines()
        for lines in lines1:
            a = lines.split(";")
            if len(a) > 2:
                rowPosition = self.dlg.tableShow.rowCount()
                self.dlg.tableShow.insertRow(rowPosition)
                self.dlg.tableShow.setItem(rowPosition, 0, QtGui.QTableWidgetItem(a[0]))
                self.dlg.tableShow.setItem(rowPosition, 1, QtGui.QTableWidgetItem(a[10]))
                self.dlg.tableShow.setItem(rowPosition, 2, QtGui.QTableWidgetItem(a[12]))
                self.dlg.tableShow.setItem(rowPosition, 3, QtGui.QTableWidgetItem(a[14]))
                
    def select_OutputFile(self):
        outputFileName = QFileDialog.getSaveFileName(self.dlg,"Set output file ",r"C:\Deane\Output","*.shp")
        self.dlg.lineOutput.setText(outputFileName)
        
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        self.dlg.tableShow.setRowCount(0)
        self.dlg.lineSelect.clear()
        self.dlg.lineOutput.clear()
        def dmtodd(d,m):    
            """Convert degrees minutes(d,m) to decimal degrees"""
            dd = float(d)+float(m)/60
            return dd
         
        def getBearing(bearing_string):
            """from string in format "S11-11E" to array of direction, degrees, and minutes [dir,d,m]"""
            b = bearing_string
        #     print b
            if b.startswith("N"):
                if b.endswith("E"):
                    d = 9
                elif b.endswith("W"):
                    d = 7
                else:
                    d = 8
            elif b.startswith("S"):
                if b.endswith("E"):
                    d = 3
                elif b.endswith("W"):
                    d = 1
                else:
                    d = 2
            elif b.startswith("E"):
                d = 6
            else:
                d = 4
            bearing = np.ones(4)
            bearing[0] = d
            if len(b) != 1:
                bearing[1] = float(b[1:3])
                bearing[2] = float(b[4:6])
            else:
                bearing[1] = 0
                bearing[2] = 0
            return bearing
             
        def getLatSign(direction):
            """define the sign of Y translation from direction"""
            lat = 1
            if direction < 4:
                lat = -1
            elif direction == 4 or direction == 6:
                lat = 0
            return lat
         
        def getDepSign(direction):
            """define the sign of X translation from direction"""
            dep = 1
            if direction%3 == 1:
                dep = -1
            elif direction % 3 == 2:
                dep = 0
            return dep
         
        def getLatDepRow(techdep_row):
            """returns the latitude and departure of a line from bearing array and distance"""
            b = techdep_row
            dist = float(techdep_row[3])/100
            angle = float(dmtodd(b[1],b[2]))
            latSign = getLatSign(b[0])
            depSign = getDepSign(b[0])
            lat = round(float(dist)*ma.cos(ma.radians(angle))*latSign,2)
            dep = round(float(dist)*ma.sin(ma.radians(angle))*depSign,2)
            row = np.array([lat,dep])
            return row
         
        def getLatDepFromLot(techdep_lot):
            """continuous use of getLatDepRow for one lot"""
            latdep = np.ones((len(techdep_lot),2))
            for i in range(len(techdep_lot)):
                latdepRow = getLatDepRow(techdep_lot[i])
                latdep[i][0] = latdepRow[0]
                latdep[i][1] = latdepRow[1]
            return latdep
        
        def getCoordsFromText(lot):
            coords = np.ones((len(lot)-1,2))
            for a in range(1,len(lot)):
                row = lot[a][0].split(";")
                coords[a-1][0] = float(row[0])
                coords[a-1][1] = float(row[1])
            return coords
        
        def getTDFromText(lot):
            techdep_lot = np.ones((len(lot)-1,4))
            length = len(lot)
            for a in range(1,length):
                row = lot[a][0].split(";")
                bearing = getBearing(row[0])
                techdep_lot[a-1][0] = bearing[0]
                techdep_lot[a-1][1] = bearing[1]
                techdep_lot[a-1][2] = bearing[2]
                techdep_lot[a-1][3] = float(row[1])
            return techdep_lot
         
        def getXYFromBase(latdep, base):
            """provides coordinates of the lot from a certain base"""
            coords = np.ones((len(latdep),2))
            coords[0][0] = base[0]+latdep[0][0]
            coords[0][1] = base[1]+latdep[0][1]
            for i in range(1,len(latdep)):
        #         print coords[i-1][0], "+", latdep[i][0]
                coords[i][0] = coords[i-1][0]+latdep[i][0]
                coords[i][1] = coords[i-1][1]+latdep[i][1]
            if round(coords[0][0],1) == round(coords[-1][0],1):
                if round(coords[0][1],1) == round(coords[-1][1],1):
                    coords[-1] = coords[0]
            return coords
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            vlayer = QgsVectorLayer('Polygon?crs=epsg:3123', 'Lot' , "memory")
            vlayer.isValid()
            vpr = vlayer.dataProvider()
            vlayer.startEditing()
            select_file = self.dlg.lineSelect.text()
            save_file = self.dlg.lineOutput.text()
            vpr.addAttributes([QgsField("Lot_No_CAD",QVariant.String),QgsField("Claimant",QVariant.String),QgsField("Cad_No",QVariant.String),QgsField("CMQuad",QVariant.String),
                              QgsField("BRGY",QVariant.String),QgsField("M_CT",QVariant.String),QgsField("PROV",QVariant.String),QgsField("ISL",QVariant.String),
                              QgsField("GE",QVariant.String),QgsField("DATE_SV",QVariant.String),QgsField("SVN_No",QVariant.String),QgsField("Lot_No_SVN",QVariant.String),QgsField("DArea",QVariant.String),QgsField("TIE",QVariant.String),QgsField("CArea",QVariant.String)])
            file = open(select_file,'r')
            lines = file.readlines()
            if self.dlg.radioTD.isChecked():
                lot = np.empty((0,1))
                for i in range(len(lines)):
                    if lines[i].count("&") == 0:
                        lot = np.vstack((lot,lines[i][:-1]))
                    else:
                        lot = np.vstack((lot,lines[i][:-2]))
                        techdep_lot = getTDFromText(lot)
    #                     techdep_lot = np.ones((len(lot)-1,4))
    #                     for j in range(1,len(lot)):
    #                         row = lot[j][0].split(",")
    #                         bearing = getBearing(row[0])
    #                         techdep_lot[j-1][0] = bearing[0]
    #                         techdep_lot[j-1][1] = bearing[1]
    #                         techdep_lot[j-1][2] = bearing[2]
    #                         techdep_lot[j-1][3] = float(row[1])
                        techdep = getLatDepFromLot(techdep_lot)
                #             print techdep
                        coord_lot = getXYFromBase(techdep,[1611134.580,503389.190])
                        points = []
                        for j in range(len(coord_lot)):
                #            print "From computation: ",coord_lot[j][1],",",coord_lot[j][0]
                            points.append(QgsPoint(coord_lot[j][1],coord_lot[j][0]))
                #            print "From extracting value: ", points[j]
                #        print points
                        poly = QgsGeometry.fromPolygon([points])
                        details = lot[0][0].split(";")
                        if coord_lot[-1][0] == coord_lot[0][0]:
                            details.append("Closed")
                        else:
                            details.append("NotClosed")
                        f = QgsFeature()
                        f.setGeometry(poly)
                        d = QgsDistanceArea()
                #             print f.geometry().asPolygon()[0]
                        area_v2 = d.measurePolygon(f.geometry().asPolygon()[0])
                        details.append(area_v2)
                        f.setAttributes(details)
                        vpr.addFeatures([f])
                        lot = np.empty((0,1))
            elif self.dlg.radioC.isChecked():
                lot = np.empty((0,1))
                for i in range(len(lines)):
                    if lines[i].count("&") == 0:
                        lot = np.vstack((lot,lines[i][:-1]))
                    else:
                        lot = np.vstack((lot,lines[i][:-2]))
                        coord_lot = getCoordsFromText(lot)
                        points = []
                        for j in range(len(coord_lot)):
                #            print "From computation: ",coord_lot[j][1],",",coord_lot[j][0]
                            points.append(QgsPoint(coord_lot[j][1],coord_lot[j][0]))
                #            print "From extracting value: ", points[j]
                #        print points
                        fileopen = open(r"C:\Deane\Output\New folder\Text1.txt",'w')
                        for k in range(len(coord_lot)):
                            fileopen.write("{0},{1}\n".format(coord_lot[k][1],coord_lot[k][0]))
                        fileopen.close()
                        poly = QgsGeometry.fromPolygon([points])
                        details = lot[0][0].split(";")
                        if coord_lot[-1][0] == coord_lot[0][0]:
                            details.append("Closed")
                        else:
                            details.append("NotClosed")
                        f = QgsFeature()
                        f.setGeometry(poly)
                        d = QgsDistanceArea()
                #             print f.geometry().asPolygon()[0]
                        area_v2 = d.measurePolygon(f.geometry().asPolygon()[0])
                        details.append(area_v2)
                        f.setAttributes(details)
                        vpr.addFeatures([f])
                        lot = np.empty((0,1))
            vlayer.commitChanges()
            _write = QgsVectorFileWriter.writeAsVectorFormat(vlayer,save_file,"UTF-8",None,"ESRI Shapefile")
            vlayer.updateFields()
            vlayer.updateExtents()
            QgsMapLayerRegistry.instance().addMapLayers([vlayer])
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
