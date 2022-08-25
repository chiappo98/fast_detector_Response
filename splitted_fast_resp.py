#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import tempfile
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
from scipy.stats import norm 
import numpy as np
import ROOT
import sys
import uuid
import xml.etree.ElementTree as ET
import drdf
import time
import argparse

def import_configuration(configfile):
    """reads configuration parameters from xml file and returns a dictionary"""
    tree = ET.parse(configfile)
    root = tree.getroot()
    configdict = dict()
    for element in root.findall('parameter'):
        name = str(element.get('name'))
        value = eval(element.get('value'), {"__builtins__": {}}, configdict)
        configdict[name] = value
    return configdict

def load_sensor_data(inFile, treekey, evn):  #arguments are: filename, camera, event
    treename = treekey.GetName()
    tree = inFile.Get(treename)             #select camera
    tree.GetEntry(evn)                      #select event
    en = np.array(tree.energy)
    t = np.array(tree.time)
    x = np.array(tree.x)
    y = np.array(tree.y)
    z = np.array(tree.z)
    sensor_data = np.vstack((en,t,x,y,z)).T
    return sensor_data, treename            #output: information on photons + camera name

def assign_channel(photons, geom):          #arguments: sensor_data, CONFIG     
    """assigns photon to corresponding matrix channel"""    
    shape = geom['matrix']                  #SiPM matrix is 32x32
    nch = shape[0] * shape[1]               #number of channels 
    xside = shape[0] * (geom['cellsize'] + 2 * geom['celledge'])/ 2         #find coordinates of matrix edge 
    yside = shape[1] * (geom['cellsize'] + 2 * geom['celledge'])/ 2         #wrt the centre of the sensor
    
    # ---- verify photons hit active areas and apply cuts ----
    z_thres = np.where(np.isclose(photons[:,4], geom['zplane']))
    active_areaX = np.where((np.abs(photons[:,2][z_thres])>=0) & (np.abs(photons[:,2][z_thres]) <= xside))
    cut1 = np.intersect1d(z_thres,active_areaX)
    
    xedge = np.remainder(np.abs(photons[:,2][cut1]),(geom['cellsize'] + geom['celledge']))        
    x_thres = np.where((xedge >= geom['celledge']) & (xedge<=(geom['cellsize']+geom['celledge'])))
    cut2 = np.intersect1d(cut1,x_thres) 
    
    active_areaY = np.where((np.abs(photons[:,3][cut2])>=0) & (np.abs(photons[:,3][cut2]) <= yside))   
    cut3 = np.intersect1d(cut2,active_areaY)    
                                                  
    yedge = np.remainder(np.abs(photons[:,3][cut3]),(geom['cellsize'] + geom['celledge']))           
    y_thres = np.where((yedge >= geom['celledge']) & (yedge<=(geom['cellsize']+geom['celledge'])))
    cut4 = np.intersect1d(cut3,y_thres)
    
    cell_x = np.floor_divide(photons[:,2][cut4],(geom['cellsize'] + 2 * geom['celledge'])) + (shape[0] / 2)
    cell_y = np.floor_divide(-photons[:,3][cut4],(geom['cellsize'] + 2 * geom['celledge'])) + (shape[1] / 2)
    time = photons[:,1][cut4]
    ch = cell_y * shape[0] + cell_x         #each channel identified by a SINGLE NUMBER from 0 to 1023
    return time, ch
    
def count_photons(time, ch, config ):                                            #argument: time, photons (a single array) , config
    """considering pde only for sipm response, for debugging/fast execution""" 
    phlist = []
    for c in range(1024):
        ph = np.where(ch==c)               #find all photons that reached channel "c"        
        if (ph[0].size!=0):                 
            tmin = np.amin(time[ph])                #arrival time of first photon
            time_cut = np.where(time[ph]<tmin+config['integrTime'])            #find all photons of the channel which arrived within integrationTime (e.g. 500ns)
            t_num = np.count_nonzero(time[ph]<tmin+config['integrTime'])  
            pde_ph = np.count_nonzero(np.random.uniform(0,1,t_num) < config['pde127nm'])      #apply the pde over the time-allowed photons
            cross_ph = np.count_nonzero(np.random.uniform(0,1,pde_ph) < config['pcross'])     #apply cross-talk over the pde-allowed photons
            nph = pde_ph + cross_ph + sum(np.random.normal(0,config['phgain'],pde_ph+cross_ph))    #count the resulting number of photons + gain on photon amp.
           
            phtimes_pde = time[time_cut[0:pde_ph]]                #extract from time array arrival times of resulting number of photons 
            phtimes_cross = time[time_cut[0:cross_ph]]            #add time of photons added with cross-talk
            phtimes = np.concatenate((phtimes_pde,phtimes_cross))                     
            if nph < 1:                                          #can be seen as a threshold on channel amplitude 
                count_result = (0, np.nan)
            else:
                count_result = (nph, tmin)                           
        else:
            count_result = (0, np.nan)
        phlist.append(count_result)     
    return phlist
             
def count_photons_no_cut(time, ch, config ):                                            
    """considers simply the total number of photons reaching each camera"""
    phlist = []
    for c in range(1024):
        ph = np.where(ch==c)               #find all photons that reached channel "c"        
        if (ph[0].size!=0):                  
            tmin = np.amin(time[ph])            #arrival time of first photon
            nph = time[ph].size               
            if nph < 1:                          #can be seen as threshold on channel amplitude
                count_result = (0, np.nan)
            else:
                count_result = (nph, tmin)                           
        else:
            count_result = (0, np.nan)
        phlist.append(count_result)         
    return phlist
            
def main_evn(inFile,klist,evn,drdffile):
         treeEv = inFile.Get(klist.Last().GetName())     #opening tree of first sensor to get idEvent
         treeEv.GetEntry(evn)                        #select event
         idEvent = treeEv.idEvent                    
         drdffile.start_event(idEvent)
         for key in klist:                           #loop over cameras (the keys of the list)
             if key.GetName() != 'commit_hash':
                 sensor_data, sensor_name= load_sensor_data(inFile, key, evn)
                 t_arr, sensor_data = assign_channel(sensor_data, CONFIG)           #output energy+time
                 if eval(nocut):
                     detected_ph_time = count_photons_no_cut(t_arr, sensor_data, CONFIG)  
                     imgshape = CONFIG['matrix']
                     img = np.asarray(detected_ph_time).reshape(imgshape[0], imgshape[1], 2).astype('float32')   #reshape the list of ph 
                     image = drdf.Image(img)
                     drdffile.add_image(sensor_name, image)
                 else: 
                     detected_ph_time = count_photons(t_arr, sensor_data, CONFIG)       #list of : nph + timeof first arrival
                     imgshape = CONFIG['matrix']
                     img = np.asarray(detected_ph_time).reshape(imgshape[0], imgshape[1], 2).astype('float32')   #reshape the list of ph 
                     image = drdf.Image(img)
                     drdffile.add_image(sensor_name, image)

         return drdffile        
    
if __name__ == '__main__':
    
    start_time = time.perf_counter()
    
    file = open(sys.argv[1],"r")
    content = file.read().splitlines()
    
    configfile = content[0]    #configuration .xml file
    fname = content[1]          #simulation output .root file
    wfile = content[2]          #output .img file
    nocut = content[3]          #count total number of photons  (True or False)
    jobNumber = int(content[4])      #number of submitted job from bash script
    jobSize = int(content[5])        #size of submitted job from bash script
    start_evn = int(content[6])      #staring event (if not 0)
    idrun = content[7]          #run identifier (UUID) (True or False)  ------------------>>>>> if True, read also line 8
        
    CONFIG = import_configuration(configfile)               #geometrical configuration
    drdffile = drdf.DRDF()
    if eval(idrun):              
        try: 
            runid = uuid.UUID(content[8])
        except ValueError:
            print('Insert valid run identifier (UUID format)')
            sys.exit()              
        drdffile.start_run(runid)
    else:
        runid = uuid.uuid1()
        drdffile.start_run(runid)
        print('run id: ', runid)
    drdffile.set_georef("DUMMY")
        
    inFile = ROOT.TFile.Open(fname, "READ")         #file sensors.root
    klist = inFile.GetListOfKeys()
    nEvents = inFile.Get(klist.Last().GetName()).GetEntries()      
    start = jobSize*jobNumber + start_evn           #defining event interval
    stop = jobSize*(jobNumber+1) + start_evn   
    if ((start > nEvents) or (stop > nEvents)):         #check whether interval is allowed
        sys.exit("ERROR. Invalid Jobnumber or Start_event")

    for evn in range(start,stop):
        drdffile=main_evn(inFile,klist,evn,drdffile)
    drdffile.write(wfile) 
    
    #print("img file saved.")
    inFile.Close()
    end_time=time.perf_counter()
    print("--- %s seconds ---" % (end_time - start_time))

    #to set up environment
    #export PYTHONPATH=/opt/exp_software/neutrino/PYTHON3_PACKAGES/
    #source /opt/exp_software/neutrino/ROOT/v6.20.00_py3/bin/thisroot.sh
