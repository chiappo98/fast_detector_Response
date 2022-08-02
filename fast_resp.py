import os
import tempfile
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
from matplotlib import pyplot as plt
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
    
    z_thres = np.where(photons[:,4]== geom['zplane'])
    xedge = np.remainder(photons[:,2][z_thres],(geom['cellsize'] + geom['celledge']))        
    x_thres = np.where((xedge >= geom['celledge']) & (xedge<=(geom['cellsize']+geom['celledge'])))
    cut1 = np.intersect1d(z_thres,x_thres)                                                      
    yedge = np.remainder(photons[:,3][cut1],(geom['cellsize'] + geom['celledge']))           
    y_thres = np.where((yedge >= geom['celledge']) & (yedge<=(geom['cellsize']+geom['celledge'])))
    cut2 = np.intersect1d(cut1,y_thres)
    
    cell_x = np.floor_divide(photons[:,2][cut2],(geom['cellsize'] + 2 * geom['celledge']) + (shape[0] / 2))
    cell_y = np.floor_divide(photons[:,3][cut2],(geom['cellsize'] + 2 * geom['celledge']) + (shape[1] / 2))
    time = photons[:,1][cut2]
    ch = cell_y * shape[0] + cell_x         #each channel identified by a SINGLE NUMBER from 0 to 1023
    return time, ch

def count_photons(time, ch, config ):                                            #argument: ph. channel, energy, time 
    """considering pde only for sipm response, for debugging/fast execution"""
    phlist = []
    for c in range(1024):
        ph = np.where(ch==c)               #find all photons that reached channel "c"        
        if (ph[0].size!=0):                  #---->>>correct??
            tmin = np.amin(time[ph])            
            time_cut = np.where(time[ph]<tmin+config['integrTime'])            #find all photons of the channel which arrived within 200ns
            t_num = np.count_nonzero(time[ph]<tmin+config['integrTime'])        
            pde_ph = np.count_nonzero(np.random.uniform(0,1,t_num) < config['pde127nm'])      #apply the pde over the time-allowed photons
            cross_ph = np.count_nonzero(np.random.uniform(0,1,pde_ph) < config['pcross'])     #apply cross-talk over the pde-allowed photons
            nph = pde_ph + cross_ph + sum(np.random.normal(0,config['phgain'],pde_ph+cross_ph))    #count the resulting number of photons + gain
           
            phtimes_pde = time[time_cut[0:pde_ph]]                               #extract from time array arrival times of resulting number of photons 
            phtimes_cross = time[time_cut[0:cross_ph]]            #add time of photons added with cross-talk
            phtimes = np.concatenate((phtimes_pde,phtimes_cross))                     #modify............
            if nph < 1:          #can be seen as threshold 
                count_result = (0, np.nan)
            else:
                count_result = (nph, tmin)                           #time of first photon (amin returns minimum value of the array)
        else:
            count_result = (0, np.nan)
        phlist.append(count_result)                                   
    return phlist

def count_photons_no_cut(photons, config ):                                            #argument: ph. channel, energy, time 
    """considers simply the total number of photons reaching each camera"""
    phlist = []
    for c in range(1024):
        ph = np.where(ch==c)               #find all photons that reached channel "c"        
        if (ph[0].size!=0):                  #---->>>correct??
            tmin = np.amin(time[ph])            
            nph = time[ph].size               #modify............
            if nph < 1:          #can be seen as threshold 
                count_result = (0, np.nan)
            else:
                count_result = (nph, tmin)                           #time of first photon (amin returns minimum value of the array)
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
         #tevent_start = time.perf_counter()
         treeEv = inFile.Get(klist.Last().GetName())     #opening tree of first sensor to get idEvent
         treeEv.GetEntry(evn)                        #select event
         idEvent = treeEv.idEvent                    
         drdffile.start_event(idEvent)
         #t0 = time.perf_counter()
         #print("processing event n. ", idEvent)
         #tot_ph = np.empty(0)
         for key in klist:                           #loop over cameras (the keys of the list)
             if key.GetName() != 'commit_hash':
                 #t0 = time.perf_counter()
                 sensor_data, sensor_name= load_sensor_data(inFile, key, evn)
                 t_arr, sensor_data = assign_channel(sensor_data, CONFIG)           #output energy+time
                 #t0 = time.perf_counter()
                 if (args.nocut):
                     detected_ph_time = count_photons_no_cut(t_arr, sensor_data, CONFIG)  
                     #t0 = time.perf_counter()
                     #n_ph = ph_num(detected_ph_time)
                     #tot_ph = np.append(tot_ph,n_ph)
                     imgshape = CONFIG['matrix']
                     img = np.asarray(detected_ph_time).reshape(imgshape[0], imgshape[1], 2).astype('float32')   #reshape the list of ph 
                     image = drdf.Image(img)
                     drdffile.add_image(sensor_name, image)
                 else: 
                     detected_ph_time = count_photons(t_arr, sensor_data, CONFIG)       #list of : nph + timeof first arrival
                     #t0 = time.perf_counter()
                     #n_ph = ph_num(detected_ph_time)
                     #tot_ph = np.append(tot_ph,n_ph)
                     imgshape = CONFIG['matrix']
                     img = np.asarray(detected_ph_time).reshape(imgshape[0], imgshape[1], 2).astype('float32')   #reshape the list of ph 
                     image = drdf.Image(img)
                     drdffile.add_image(sensor_name, image)
         #print("execution time for event {1}: {0:.5f} s".format(t0 - tevent_start , evn))
         #print("number of ph=",np.sum(tot_ph))
         return drdffile        
    
if __name__ == '__main__':
    
    start_time = time.perf_counter()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('configfile', help = 'configuration .xml file')
    parser.add_argument('rootfile', help = 'simulation output .root file')
    parser.add_argument('outfile', help = 'output .img file')
    parser.add_argument('-nc', '--nocut', action ='store_true', help = ' count total number of photons')
    parser.add_argument('-e', '--events', help = ' max number of events to be processed')
    parser.add_argument('-i', '--idrun', help ='run identifier (UUID)')         #????
    args = parser.parse_args()

    configfile = args.configfile
    fname = args.rootfile    
    wfile = args.outfile
    
    CONFIG = import_configuration(configfile)               #geometrical configuration
    drdffile = drdf.DRDF()
    if args.idrun:              #??
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
#---------------------------------------------------------------------------------------------------------
        
    inFile = ROOT.TFile.Open(fname, "READ")         #file sensors.root
    klist = inFile.GetListOfKeys()
    nEvents = inFile.Get(klist.Last().GetName()).GetEntries()      
    if (args.events):                               
        if int(args.events) < nEvents:
            nEvents = int(args.events)

    for evn in range(nEvents):                      #loop over events
        drdffile=main_evn(inFile,klist,evn,drdffile)
    drdffile.write(wfile) 
    
    #print("img file saved.")
    inFile.Close()
    end_time=time.perf_counter()
    print("--- %s seconds ---" % (end_time - start_time))

    #to set up environment
    #export PYTHONPATH=/opt/exp_software/neutrino/PYTHON3_PACKAGES/
    #source /opt/exp_software/neutrino/ROOT/v6.20.00_py3/bin/thisroot.sh