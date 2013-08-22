import os

etcDir = '/opt/owtg/etc/'
sFilename = etcDir+'sensors'
adbFilename = etcDir+'archive.rrd'
gdbFilename = etcDir+'graphing.rrd'

def getLines(filename):
    file_ = open(filename,'r') #Open file for reading
    lineList = file_.readlines()
    lineList_ = []
    file_.close()
    
    #Ignore comments (lines beginning with #)
    for line in lineList:
        if line.startswith('#'):
            continue
        if line:
            #Strip newlines
            line = line.rstrip('\n')
            lineList_.append(line)
    return lineList_            

class OWTGSensor:
    address = ''
    alias = ''
    minAlarm = 0.0
    maxAlarm = 0.0
    graph = False

def getSensors():
    dSensors = [] #Already discovered sensors
    
    lineList = getLines(sFilename)

    for line in lineList:
        if line:
            params = line.split(':')
            newSensor = OWTGSensor()
            newSensor.alias = params[0]
            newSensor.address = params[1]
            newSensor.minAlarm = float(params[4])
            newSensor.maxAlarm = float(params[5])
            if params[3] == 'y':
                newSensor.graph = True
            dSensors.append(newSensor)
    return dSensors
    
def dbExists():
    exists = True
    if not os.path.exists(adbFilename) or not os.path.exists(gdbFilename):
        exists = False
    return exists
