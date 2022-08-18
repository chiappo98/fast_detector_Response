import drdf
import uuid
import numpy as np
import argparse
import sys
import os
import ROOT
from matplotlib import pyplot as plt
import pandas as pd

def read_file(drdf_file):
    testfile = drdf.DRDF()
    testfile.read(drdf_file)
    event_list = []
    for run, rundata in testfile.runs.items():
      #print('Run', run, 'with', len(rundata), 'events')
      #print(' with geometry', rundata.georef)
      ev_arr = np.empty(0)
      event_amp = np.empty(0)
      for event, eventdata in rundata.items():
        print('Event', event, 'with', len(eventdata), 'images')
        cam_amp = np.empty(0)
        px_amp = np.empty(0)
        for src, image in eventdata.items():
          #print('Image from source', src, 'with size', image.pixels.amplitude)
          amp = image.pixels[:,:,0].flatten()      #(32,32)matrix reshaped into 1d array of lenght 1024
          px_amp = np.append(px_amp,amp)
          cam_amp = np.append(cam_amp,np.sum(amp))                #put together all cameras  px_amp.shape(1024*76,)=(77824,)
        ev_arr = np.append(ev_arr,event)
        event_amp = np.append(event_amp,np.sum(cam_amp))
        event_list.append((event, px_amp))
    events = np.column_stack((ev_arr,event_amp))
    return event_list, events                         

def load_sensor_data(inFile, treekey, evn):  #arguments are: filename, camera, event
    treename = treekey.GetName()
    tree = inFile.Get(treename)             #select camera
    #print(treename)
    #sensor_data = np.empty((0,5),float)
    tree.GetEntry(evn)                      #select event
    sensor_energy = np.array(tree.energy)    
    return sensor_energy, treename            #output: information on photons + camera name
    
        
if __name__ == '__main__':

    #parser = argparse.ArgumentParser()    
    drdf_calo='/home/NEUTRINO/chiappon/calorimetry/calo_2reduced/response_cut.drdf'
    sensor_file = '/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-OPTICALSIM-PROD/GRAIN/test_fast_chiappo/sensors.root'
    output_path="/home/NEUTRINO/chiappon/calorimetry/calo_2test"
    jobSize = 1
    jobNumber = 2        #number of total jobs
    start_evn = 0
    
    if not os.path.exists(output_path):
        os.mkdir(output_path)
#---------- read drdf file ------------------------------------------------------------------------------    
    print('Reading drdf file')
    event_list, event_array=read_file(drdf_calo)    
    
    event_num = event_array[:,0]
    event_amp = event_array[:,1]

    #----- plot photon amplitude distribution for each camera -----------   
    #ATTENTION: this step may take a long time    
    plot_cameras = True
    if plot_cameras:
      evn_path = output_path+'/cameras_folder'
      if not os.path.exists(evn_path):        #create 
        os.mkdir(evn_path)
      npix = 1024
      for ev, amp_calo in event_list:           #loop over events
        print("Event",ev)
        cam_path = evn_path+'/event'+str(ev)
        if not os.path.exists(cam_path):        #create 
          os.mkdir(cam_path)            
        for i in range(int(amp_calo.size/npix)):                            #separate each camera
          amp1 = np.reshape(amp_calo[npix*i:npix*(i+1)],(32,32))
          plt.pcolormesh(amp1)
          plt.colorbar()
          plt.savefig(cam_path+"/cam"+str(i+1)+".png")
          plt.close()

#---------- read sensor file ------------------------------------------------------------------------------    
    print('Reading sensors.root')
    inFile = ROOT.TFile.Open(sensor_file, "READ")         #file sensors.root
    klist = inFile.GetListOfKeys()
    stop = jobSize*jobNumber + start_evn  
    event_energy = np.empty(0)
    for evn in range(start_evn,stop):
       print('Event',evn)
       treeEv = inFile.Get(klist.Last().GetName())     #opening tree of first sensor to get idEvent
       treeEv.GetEntry(evn)                            #select event
       cameras_energy = np.empty(0)
       for key in klist:                           #loop over cameras (the keys of the list)
            if key.GetName() != 'commit_hash':
                sensor_energy, sensor_name= load_sensor_data(inFile, key, evn)
                cameras_energy = np.append(cameras_energy,np.sum(sensor_energy))
       event_energy = np.append(event_energy,np.sum(cameras_energy))
       
    #plt.plot(event_num,event_amp,'-o',label='number of photons')
    #plt.plot(event_num,event_energy,'-o',label='energy')
    #plt.legend(loc='upper right')
    #plt.savefig(output_path+"/event_amplitude.png")
    #plt.close()
    
    plt.loglog(event_energy,event_amp,'*')
    plt.xlabel("energy")
    plt.ylabel("number of photons")      
    plt.savefig(output_path+"/LOGenergyVamplitude.png")
    plt.close()
    
    plt.plot(event_energy,event_amp,'*')
    plt.xlabel("energy")                    #unit of energy ????????????????
    plt.ylabel("number of photons")                  
    plt.savefig(output_path+"/energyVamplitude.png")
    plt.close()