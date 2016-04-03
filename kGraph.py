#k-Nearest Neighbor Graph algorithm for Qgis
#author: Roman Kuchukov, rk.arch@yandex.ru
#to run -- 1. save empty layer (lines) to outLayerPath, 2. select input point layer, 3. run script and view notes

#output file paths 
outLayerPath = u'E:/QGIS/myData/kGraph.shp'
outLayerName = 'kGraph'
outTxtPath = u'E:/QGIS/myData/kGraphLog.txt'

#list of log strings 
listLog = []
#active layer
layer = iface.activeLayer()
#output layer with graph
vectorLyr = QgsVectorLayer(outLayerPath, outLayerName , "ogr")



#add field "fieldNm" to input  layer 
def addField (layer, fieldNm):
    from PyQt4.QtCore import QVariant #to add top-Field
    vpr = layer.dataProvider() 
    vpr.addAttributes([QgsField(fieldNm, QVariant.Int)])
    layer.updateFields()
    print ("DONE: added text field", fieldNm)

#add Qgis ID to input  layer 
def AddID(layer, fieldNm):
    print('Layer loaded: ', layer.isValid(), "adding Qgis ID") 
    layer.startEditing()
    addField(layer, fieldNm)
    for feature in layer.getFeatures():
        feature[fieldNm] = feature.id()
        layer.updateFeature(feature)
    layer.commitChanges()
    print "Qgis id added"

#request by ID
def iterID(fid):
    ptsCoord = []
    request = QgsFeatureRequest().setFilterFids(fid)
    iter = layer.getFeatures(request)
    for i in iter:
        #print i.id()
        #print i.geometry().asPoint()
        ptsCoord.append(i.geometry().asPoint())
    return ptsCoord
    
#draw line
def drawLine(points):
    vpr = vectorLyr.dataProvider()
    line = QgsGeometry.fromPolyline(points)
    f = QgsFeature()
    f.setGeometry(line)
    vpr.addFeatures([f])
    vectorLyr.updateExtents()
    return f

#create Spatial Index
def SIndex():
    fts = layer.getFeatures() 
    first = fts.next()
    index = QgsSpatialIndex()
    for f in fts:
        index.insertFeature(f)
    print "Spatial Index created"
    return index

#select nearest neibhors
def Nhood(index, idInput, k):
    layer.setSelectedFeatures([]) #deselect
    points = []
    pointInput = iterID([idInput])
    hood = index.nearestNeighbor(pointInput[0], k+1)
    #print("hood ", hood)
    print "%i, hood k=%i, " % (idInput, k), ". ".join( str(e) for e in hood) #without [ ]
    for h in hood:
        layer.select(h)
        points = iterID([idInput, h])
    iface.mapCanvas().zoomToSelected()
    return hood

#draw hub
def HUBhood(index, idInput, k):
    points = []
    pointInput = iterID([idInput])
    hood = index.nearestNeighbor(pointInput[0], k+1)
    print idInput
    txtIO = str("%i, %i, " % (idInput, k),) + str(". ".join( str(e) for e in hood[1:])) #without self element
    AddTxt(listLog, txtIO)
    for h in hood:
        #layer.select(h)
        points = iterID([idInput, h])
        drawLine(points)
    #iface.mapCanvas().zoomToSelected()
    return hood[1:]

#main function
def kGraph(index, layer, k):
    listLog = []
    fts = layer.getFeatures()
    print "computing Qid:"
    for f in fts:
        #print f.id()
        HUBhood(indx, f.id(), k)
    print "kGraph - DONE"
 

#text functions
def AddTxt(string, txtIO):
    string.append(txtIO)
    
def log():
    for i in listLog:
        print i

def saveLog():
    count = 0
    output_file = open(outTxtPath, 'w') 
    line = "#, Qid, k-Neighbors, hood\n"
    unicode_line = line.encode('utf-8')
    output_file.write(unicode_line)
    for i in listLog:
        line = "%i, %s\n" %(count, i)
        unicode_line = line.encode('utf-8')
        output_file.write(unicode_line)
        count = count +1
    output_file.close()
    print "log saved to %s" %outTxtPath

#RUN script

print "# RUNNING k-Nearest Points Graph algorithm #\n# SELECT input point layer #\n***"
indx = SIndex()  # create Spatial Index
print "result file path", outLayerPath
print '1. To add Qgis ID on input layer type:\n\tAddID(layer, "Qid")  # "Qid" - name of field - example'
print '2. To view nearest points, type:\n\tNhood(indx, 1, 4)  # 1- Qid, 4 - links - example' 
print '3. To add hub lines - manualliy, type:\n\tHUBhood(indx, 1, 4)  # 1- Qid, 4 - links - example'
print '4. To start building graph(s) - automatically, SELECT INPUT layer, type:\n\tkGraph(indx, layer, 4)  # 4 - links - example\n*** '
print '5. To view log type: log() ; to save log type: saveLog()'