#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""

    This python script reads two input VR particle catalog files and quickly compares them. It determines
    if the catalogs match. If they do not, further tests are run. For a perfect match, particles are in the
    same order. Information is passed to the script via a simple text file that has the following format
    VRrefbasefilename VRrefinputformat
    VRcompbasefilename VRcompinputformat
    
"""


import sys,os,string,time,re,struct
from subprocess import call
import numpy as np

#load VR python routines
pathtovelociraptor=sys.argv[0].split('examples')[0]
sys.path.append(pathtovelociraptor+'/tools/')
import velociraptor_python_tools as vpt

def PerfectCrossMatch(VRdata):
    iflag1 = (VRdata['ref']['properties']['num'] != VRdata['comp']['properties']['num'])
    iflag2 = (VRdata['ref']['particles']['Npart'].size != VRdata['comp']['particles']['Npart'].size)    
    if (iflag1):
        print('Catalog contains different number of objects ... Not perfect match')
    if (iflag2): 
        print('Particle catalog contains different number of particles ... Not perfect match')
    if (iflag1 or iflag2):
        return 0
    num = VRdata['ref']['particles']['Npart'].size
    ref = np.concatenate(VRdata['ref']['particles']['Particle_IDs'])
    comp = np.concatenate(VRdata['comp']['particles']['Particle_IDs'])
    if (np.array_equal(ref,comp)):
        if (np.where(np.isin(ref,comp))[0].size == num):
            print('Particle catalog contains same number of particles but IDs in different order ... Not perfect match but close')
            return 1
        else:
            print('Particle catalog contains same number of particles but IDs differ ... Not perfect match')
            return 0
    return 2
        
def CheckProperties(VRdata):
    iflag1 = (VRdata['ref']['properties']['num'] != VRdata['comp']['properties']['num'])
    iflag2 = (VRdata['ref']['particles']['Npart'].size != VRdata['comp']['particles']['Npart'].size)
    proplist = ['Mass_tot', 'Vmax']    
    if (iflag1 == True):
        return 0
    partdiff = np.zeros(VRdata['ref']['properties']['num'], dtype = np.int32)
    propdiff = np.zeros(VRdata['ref']['properties']['num'], dtype = np.int32)
    num = VRdata['ref']['properties']['num']
    #number of objects the same but particle list ordered differently
    time1 = time.clock()
    for i in range(num):
        if not np.array_equal(VRdata['ref']['particles']['Particle_IDs'][i], VRdata['comp']['particles']['Particle_IDs'][i]):
            partdiff[i] = 1
        for prop in proplist:    
            if (VRdata['ref']['properties'][prop][i] != VRdata['comp']['properties'][prop][i]):
                propdiff[i] = 1
    numpartdiff = np.sum(partdiff)
    numpropdiff = np.sum(propdiff)    
    print('Finished processing individual objects in ', time.clock()-time1)
    if (numpartdiff > 0):
        print('Difference in particles', numpartdiff, ' of', num)
    if (numpropdiff > 0):
        print('Difference in properties', numpropdiff, ' of', num)
    if (numpropdiff == 0 and numpartdiff > 0):
        print('Difference in order of particles but not resulting properties, nor number of particles in each object')
        return 1
    return 0

#if __name__ == '__main__':

print('Running', sys.argv[0])
print('Input is file name of config file')
print('Config file should contain the following')
print('VRrefbasefilename VRrefinputformat')
print('VRcompbasefilename VRcompinputformat')

if (os.path.isfile(sys.argv[1])==False):
    print("Missing input info file",sys.argv[1])
    exit(1)

#load the plot info file,
print("Reading reference VR file", sys.argv[1])
infofile=open(sys.argv[1], 'r')
VRdata = {'label': None}

time1=time.clock()
for label in ['ref', 'comp']:
    data = infofile.strip().split(' ')
    VRdata[label]= {'filename': None, 'inputformat': None, 'particles': None, 'properties': None, 'num': 0}
    VRdata[label]['filename'], VRdata[label]['inputformat'] = data[0], np.int32(data[1])
    print('Reading ',label,' stored in ',VRdata[label]['filename'])
    VRdata[label]['particles'] = ReadParticleDataFile(VRdata[label]['filename'], VRdata[label]['inputformat'])
    VRdata[label]['properties'], numhalos = ReadPropertyFile(VRdata[label]['filename'], VRdata[label]['inputformat'])
    VRdata[label]['num'] = numhalos

print('Finished reading information', time.clock()-time1)
print('Checking for perfect match')
iflag = PerfectCrossMatch(VRdata)
if (iflag == 1):
    CheckProperties(VRdata)

# Return an overall PASS or FAIL
if iflag == 0:
    print('\n*********************')
    print('* Comparison FAILED *')
    print('*********************\n')
    exit(1)
else:
    print('\n*********************')
    print('* Comparison PASSED *')
    print('*********************\n')
    exit(0)

