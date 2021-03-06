#!/usr/bin/python
#   Copyright (C) 2013 OHRI 
#
#   This file is part of OWTG.
#
#   OWTG is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OWTG is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OWTG.  If not, see <http://www.gnu.org/licenses/>.

import ownet
import rrdtool
from owtg import *
from time import localtime, mktime
from os import path

if datGet('allowRun') != '1':
    exit(0)
    
if not path.exists(sFilename):
    sFile = open(sFilename,'w+')
    sFile.close()
    chmod(sFilename,0666)

ownet.init('localhost:4304')

dAddresses = [s.address for s in getSensors()] #already discovered addresses
gAddresses = [s.address for s in getSensors() if s.graph == True] #Addresses with "graph" turned on
newAddresses = [] #new addresses found during this run
newFile = [] #array of lines to write out to file
newFile.append(sFileTop) #Add comments to top of file

sFile = open(sFilename,'r') #discovered file, open for reading
lineList = sFile.readlines()
sFile.close()

for line in lineList:
    if line.startswith('#'):
        continue
    newFile.append(line)

for directory in ownet.Sensor('/','localhost',4304).sensorList():
    seen = False
    address = None
    #exclude "simultaneous" as it has a temperature file but is not a sensor
    if directory == ownet.Sensor('/simultaneous','localhost',4304):
        continue

    #If the directory contains "temperature", it is a sensor
    if hasattr(directory,'temperature'):
        #store the address
        address = directory.address
        for a in dAddresses:
            #check against every discovered addresss
            if address == a:
                seen = True
                break
        #if the address has not been already discovered, add it to newAddresses
        if not seen:
            newAddresses.append(address)

for a in newAddresses:
    #Build a string in the form of "[alias(empty)]:[address]:[timestamp]:[graph(y/n)]:[min-alarm]:[max-alarm]:[lasttemp]\n"
    sensorLine = ':' + a + ':' + str(int(mktime(localtime()))) + ':y:20:30:NaN\n'
    #Append it to the new file line array
    newFile.append(sensorLine)

if dbExists():
    for a in gAddresses:
        claimed = False #Has it been claimed in the RRD?
        foundUnclaimed = False #Has an unclaimed DS been found?
        firstUnclaimed = '-1' #ID of the first seen unclaimed DS
        for dsName in rrdtool.fetch(adbFilename, 'AVERAGE')[1]:
            if dsName == a:
                claimed = True
            if dsName.split('_')[0] == 'unclaimed' and not foundUnclaimed:
                foundUnclaimed = True
                firstUnclaimed = dsName.split('_')[1]
        if not claimed:
            rrdtool.tune(adbFilename, '--data-source-rename', 'unclaimed_'+firstUnclaimed+':'+a)
            rrdtool.tune(gdbFilename, '--data-source-rename', 'unclaimed_'+firstUnclaimed+':'+a)

newFile.sort()  #Sort the sensors alphabetically, by alias (first param on the line)
sFile = open(sFilename,'w') #sensors file, open for writing
sFile.writelines(newFile)
sFile.close()

