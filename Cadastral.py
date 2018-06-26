# Customize this starter script by adding code
# to the run_script function. See the Help for
# complete information on how to create a script
# and use Script Runner.
""" Your Description of the script goes here """

# Some commonly used imports
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import numpy as np, math as ma, re, openpyxl

def dmtodd(d,m):
    dd = float(d)+float(m)/60
    return dd

def getBearing(bearing_string):
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
    lat = 1
    if direction < 4:
        lat = -1
    elif direction == 4 or direction == 6:
        lat = 0
    return lat

def getDepSign(direction):
    dep = 1
    if direction%3 == 1:
        dep = -1
    elif direction % 3 == 2:
        dep = 0
    return dep

def getLatDepRow(techdep_row):
    b = techdep_row
    dist = float(techdep_row[3])/100
    angle = float(dmtodd(b[1],b[2]))
    latSign = getLatSign(b[0])
    depSign = getDepSign(b[0])
    lat = float(dist)*ma.cos(ma.radians(angle))*latSign
    dep = float(dist)*ma.sin(ma.radians(angle))*depSign
    row = np.array([lat,dep])
    return row

def getLatDepFromLot(techdep_lot):
    latdep = np.ones((len(techdep_lot),2))
    for i in range(len(techdep_lot)):
        latdepRow = getLatDepRow(techdep_lot[i])
        latdep[i][0] = latdepRow[0]
        latdep[i][1] = latdepRow[1]
    return latdep

def getXYFromBase(latdep):
    coords = np.ones((len(latdep),2))
    coords[0][0] = 20000.00+latdep[0][0]
    coords[0][1] = 20000.00+latdep[0][1]
    for i in range(1,len(latdep)):
#         print coords[i-1][0], "+", latdep[i][0]
        coords[i][0] = coords[i-1][0]+latdep[i][0]
        coords[i][1] = coords[i-1][1]+latdep[i][1]
    if round(coords[0][0],0) == round(coords[-1][0],0):
        if round(coords[0][1],0) == round(coords[-1][1],0):
            coords[-1] = coords[0]
    return coords

def run_script(iface):
    vlayer = QgsVectorLayer('Polygon?crs=epsg:3123', 'Lot' , "memory")
    vlayer.isValid()
    vpr = vlayer.dataProvider()
    vpr.addAttributes([QgsField("Claimant",QVariant.String),QgsField("Lot_No",QVariant.String),QgsField("Title_No",QVariant.String),QgsField("Surv_No",QVariant.String),
                      QgsField("P_Surv",QVariant.String),QgsField("BRGY",QVariant.String),QgsField("M_CT",QVariant.String),QgsField("PROV",QVariant.String),
                      QgsField("RGN",QVariant.String),QgsField("GE",QVariant.String),QgsField("TiePt",QVariant.String),QgsField("DArea",QVariant.String),QgsField("Lot_Stat",QVariant.String),QgsField("CArea",QVariant.Double)])
    file = open(r"C:\Deane\Data\Trial.txt")
    lines = file.readlines()
    lot = np.empty((0,1))
    for i in range(len(lines)):
        if lines[i].count("&") == 0:
            lot = np.vstack((lot,lines[i][:-1]))
        else:
            lot = np.vstack((lot,lines[i][:-2]))
#             print lot
            techdep_lot = np.ones((len(lot)-1,4))
            for j in range(1,len(lot)):
                row = lot[j][0].split(",")
                bearing = getBearing(row[0])
                techdep_lot[j-1][0] = bearing[0]
                techdep_lot[j-1][1] = bearing[1]
                techdep_lot[j-1][2] = bearing[2]
                techdep_lot[j-1][3] = float(row[1])
            techdep = getLatDepFromLot(techdep_lot)
#             print techdep
            coord_lot = getXYFromBase(techdep)
            points = []
            for j in range(len(coord_lot)):
                print "From computation: ",coord_lot[j][1],",",coord_lot[j][0]
                points.append(QgsPoint(coord_lot[j][1],coord_lot[j][0]))
                print "From extracting value: ", points[j]
            print points
            poly = QgsGeometry.fromPolygon([points])
            details = lot[0][0].split(",")
            if coord_lot[-1][0] == coord_lot[0][0]:
                details.append("Closed")
            else:
                details.append("NotClosed")
            f = QgsFeature()
            f.setGeometry(poly)
            print poly
            d = QgsDistanceArea()
#             print f.geometry().asPolygon()[0]
            area_v2 = d.measurePolygon(f.geometry().asPolygon()[0])
            details.append(area_v2)
            f.setAttributes(details)
            vpr.addFeatures([f])
            lot = np.empty((0,1))
    _write = QgsVectorFileWriter.writeAsVectorFormat(vlayer,r"C:\Deane\Output\Lot.shp","UTF-8",None,"ESRI Shapefile")
    vlayer.updateFields()
    vlayer.updateExtents()
    QgsMapLayerRegistry.instance().addMapLayers([vlayer])
            
