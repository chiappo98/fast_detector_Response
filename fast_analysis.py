#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import drdf
import uuid
import numpy as np
import argparse
import sys
import os
import ROOT
from matplotlib import pyplot as plt
from scipy import optimize

def read_file(drdf_file):
    testfile = drdf.DRDF()
    testfile.read(drdf_file)
    event_list = []
    for run, rundata in testfile.runs.items():
      ev_arr = np.empty(0)
      event_amp = np.empty(0)
      for event, eventdata in rundata.items():
        print('Event', event, 'with', len(eventdata), 'images')
        cam_amp = np.empty(0)
        px_amp = np.empty(0)
        for src, image in eventdata.items():
          amp = image.pixels[:,:,0].flatten()      #(32,32)matrix reshaped into 1d array of lenght 1024
          px_amp = np.append(px_amp,amp)
          cam_amp = np.append(cam_amp,np.sum(amp))                #put together all cameras  px_amp.shape(1024*76,)=(77824,)
        ev_arr = np.append(ev_arr,event)
        event_amp = np.append(event_amp,np.sum(cam_amp))
        event_list.append((event, px_amp))
    events = np.column_stack((ev_arr,event_amp))
    return event_list, events                         
    
def load_edep_data(inFile, treekey, evn):  #arguments are: filename, camera, event
    treename = treekey.GetName()
    tree = inFile.Get(treename)             #select camera
    tree.GetEntry(evn)                      #select event
    energy_dep = 0
    for hit in tree.Event.SegmentDetectors["LArHit"]:
      energy_dep+=hit.GetEnergyDeposit()       
    return energy_dep            #output: information on photons 
            
if __name__ == '__main__':
   
    drdf_calo = sys.argv[1]
    edep_file = sys.argv[2]
    output_path = sys.argv[3]
    event_number = int(sys.argv[4])      #number of total jobs
    start_evn = int(sys.argv[5])
    plot_cameras = (sys.argv[6]).lower() in ['yes']
    
    if not os.path.exists(output_path):
        os.mkdir(output_path)
#---------- read drdf file ------------------------------------------------------------------------------    
    print('Reading drdf file')
    event_list, event_array=read_file(drdf_calo)    
    
    event_num = event_array[:,0]
    event_amp = event_array[:,1]

    #----- plot photon amplitude distribution for each camera -----------   
    #ATTENTION: this step may take a long time    
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
          plt.title("event "+str(ev)+" - camera "+str(i+1))
          plt.savefig(cam_path+"/cam"+str(i+1)+".png")
          plt.close()

#--------- read edepsim ----------------------------------------------------------------------------------
    print('Reading edepsim file')
    inFile = ROOT.TFile.Open(edep_file, "READ")         #file sensors.root
    klist = inFile.GetListOfKeys()
    stop = event_number + start_evn      
    event_energy_dep = np.empty(0)
    for evn in range(start_evn,stop):
       print('Event',evn)
       treeEv = inFile.Get(klist.Last().GetName())     #opening tree of first sensor to get idEvent
       treeEv.GetEntry(evn)                            #select event
       key = klist[2]
       if key.GetName() == 'EDepSimEvents':
           energy_dep= load_edep_data(inFile, key, evn)
           event_energy_dep = np.append(event_energy_dep,energy_dep)    
    
    #compare number of photons versus event energy
    plt.plot(event_energy_dep,event_amp,'.')
    plt.xlabel("energy (MeV)")                    #(MeV)
    plt.ylabel("number of photons")              
    plt.savefig(output_path+"/amplitudeVenergy.png")
    plt.close()

    #compare and fit event energy versus number of photons    
    def fit_func(x,m,q):
      return m*x + q
    popt, pcov = optimize.curve_fit(fit_func, event_amp, event_energy_dep,p0=[1000, 0])
    
    m = popt[0]
    q = popt[1]
    mErr = pcov[0,0]**0.5
    qErr = pcov[1,1]**0.5
    print("fit parameters")
    print("m =", m, "+/-", mErr)
    print("q =", q, "+/-", qErr)

    plt.plot(event_amp,event_energy_dep,'.',label='Data')
    plt.plot(event_amp, fit_func(event_amp, m, q),label='fit: m=%5.3f, q=%5.3f' % tuple(popt))

    plt.ylabel("energy (MeV)")                    #(MeV)
    plt.xlabel("number of photons") 
    plt.legend(loc='best')                 
    plt.savefig(output_path+"/energyVamplitude.png")
    plt.close()    
