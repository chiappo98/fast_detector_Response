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
    #print(treename)
    #sensor_data = np.empty((0,5),float)
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

def count_photons(time, ch, config ):                                            #argument: time, photons (a single array), config
    """considering pde only for sipm response, for debugging/fast execution"""
    phlist = []
    for c in range(1024):
        ph = np.where(ch==c)               #find all photons that reached channel "c"        
        if (ph[0].size!=0):                  
            tmin = np.amin(time[ph])            
            time_cut = np.where(time[ph]<tmin+config['integrTime'])            #find all photons of the channel which arrived within integrationTime (e.g. 500ns)
            t_num = np.count_nonzero(time[ph]<tmin+config['integrTime'])        
            pde_ph = np.count_nonzero(np.random.uniform(0,1,t_num) < config['pde127nm'])      #apply the pde over the time-allowed photons
            cross_ph = np.count_nonzero(np.random.uniform(0,1,pde_ph) < config['pcross'])     #apply cross-talk over the pde-allowed photons
            nph = pde_ph + cross_ph + sum(np.random.normal(0,config['phgain'],pde_ph+cross_ph))    #count the resulting number of photons + gain over photon amp.
           
            phtimes_pde = time[time_cut[0:pde_ph]]                          #extract from time array arrival times of resulting number of photons 
            phtimes_cross = time[time_cut[0:cross_ph]]                      #add time of photons added with cross-talk
            phtimes = np.concatenate((phtimes_pde,phtimes_cross))                     
            if nph < 1:          #can be seen as threshold 
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
            if nph < 1:          #can be seen as threshold 
                count_result = (0, np.nan)
            else:
                count_result = (nph, tmin)                     
        else:
            count_result = (0, np.nan)
        phlist.append(count_result)         
    return phlist

def ph_num(phlist):
    pharr = np.asarray(phlist)
    sum = np.sum(pharr.T[0])
    #print("number of ph=",sum)
    return sum
            
def main_evn(inFile,klist,evn,drdffile):
         treeEv = inFile.Get(klist.Last().GetName())     #opening tree of first sensor to get idEvent
         treeEv.GetEntry(evn)                           #select event
         idEvent = treeEv.idEvent                    
         drdffile.start_event(idEvent)
         tot_ph = np.empty(0)
         for key in klist:                           #loop over cameras (the keys of the list)
             if key.GetName() != 'commit_hash':
                 sensor_data, sensor_name= load_sensor_data(inFile, key, evn)
                 t_arr, sensor_data = assign_channel(sensor_data, CONFIG)           
                 if (args.nocut):
                     detected_ph_time = count_photons_no_cut(t_arr, sensor_data, CONFIG)            #list of : nph + timeof first arrival
                     n_ph = ph_num(detected_ph_time)
                     tot_ph = np.append(tot_ph,n_ph)
                     imgshape = CONFIG['matrix']
                     img = np.asarray(detected_ph_time).reshape(imgshape[0], imgshape[1], 2).astype('float32')   #reshape the list of ph 
                     image = drdf.Image(img)
                     drdffile.add_image(sensor_name, image)
                 else: 
                     detected_ph_time = count_photons(t_arr, sensor_data, CONFIG)       
                     n_ph = ph_num(detected_ph_time)
                     tot_ph = np.append(tot_ph,n_ph)
                     imgshape = CONFIG['matrix']
                     img = np.asarray(detected_ph_time).reshape(imgshape[0], imgshape[1], 2).astype('float32')    
                     image = drdf.Image(img)
                     drdffile.add_image(sensor_name, image)
         print("number of ph=",np.sum(tot_ph))
         return drdffile        
    
if __name__ == '__main__':
    
    start_time = time.perf_counter()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('configfile', help = 'configuration .xml file')
    parser.add_argument('rootfile', help = 'simulation output .root file')
    parser.add_argument('outfile', help = 'output .img file')
    parser.add_argument('-nc', '--nocut', action ='store_true', help = ' count total number of photons')
    parser.add_argument('-e', '--events', help = ' max number of events to be processed')
    parser.add_argument('-s', '--start_event', help = ' starting event')
    parser.add_argument('-i', '--idrun', help ='run identifier (UUID)')         
    args = parser.parse_args()

    configfile = args.configfile
    fname = args.rootfile    
    wfile = args.outfile
    
    CONFIG = import_configuration(configfile)               #geometrical configuration
    drdffile = drdf.DRDF()
    if args.idrun:              
        try: 
            runid = uuid.UUID(args.idrun)
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
    start = 0
    stop = nEvents
    if (args.events):                               
        if int(args.events) < nEvents:
            stop = int(args.events)
            if (args.start_event):    
                start = int(args.start_event)
                stop = int(args.start_event) + int(args.events)
                if ((start > nEvents) or (stop > nEvents)): 
                    sys.exit("ERROR. Invalid Jobnumber or Start_event") 

    for evn in range(start, stop):                      #loop over events
        drdffile=main_evn(inFile,klist,evn,drdffile)
    drdffile.write(wfile) 
    
    #print("img file saved.")
    inFile.Close()
    end_time=time.perf_counter()
    print("--- %s seconds ---" % (end_time - start_time))

    #to set up environment
    #export PYTHONPATH=/opt/exp_software/neutrino/PYTHON3_PACKAGES/
    #source /opt/exp_software/neutrino/ROOT/v6.20.00_py3/bin/thisroot.sh
