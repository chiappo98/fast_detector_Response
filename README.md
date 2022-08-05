# Table of contents
- [Fast detector response](#fast-detector-response)
- [The physics case](#the-physics-case)
- [Running the script](#running-the-script)
  - [Account request](#account-request)
  - [Required softwares](#required-softwares)
    - [The drdf module](#the-drdf-module)
  - [Fast_resp installation](#fast_resp-installation)
  - [Launching a production](#launching-a-production)
- [HTCondor](#htcondor)


# Fast detector response

The aim of this program is to simulate the Readout system of a detector composed by Silicon Photomultiplier (SiPM) sensors. They are arranged in 76 matrices (called cameras) of 32x32 sensors each, covering the internal walls of a vessel containing a scintillating material. Their scope is to detect the scintillation light produced by a charged particle moving inside the scintillating material. Using this program you can perform a calorimetric measurement, obtaining the energy of the incoming particle.

The program gives as output the distribution of photons on each camera, in a drdf file, which is a castom image format (more on this later).

# The physics case
The DUNE experiment is a long-baseline neutrino experiment which is under construction in the US between the Fermilab, where the neutrino beam will be generated, and hte Stanford Underground Research Facility in South Dakota.
The experiment will study neutrino oscillations trying to measure the $\delta_{cp}$ phase of the PMNS matrix and the neutrino mass ordering. It will also be able to detect cosmic neutrinos, providing important information about cosmic ray sources, useful for multimessenger astrophysics.

DUNE is composed by a Near Detector (ND) and a Far Detector (FD), consisting of a large TPC filled with liquid Argon. The ND has the scope of monitoring the neutrino beam just after its generation and is composed of three sub-detectors: GasAr-TPC, , and the SAND detector.

SAND in turn has three modules enclosed in a superconducting magnet: a Straw Tube Tracker, an electromagnetic calorimeter and GRAIN.

The GRAIN (GRanular Argon fot Interctions of Neutrinos) module, part of the SAND (System for on-Axis Neutrino Detection) detector of the DUNE experiment, a long-baseline experiment for the detection of artificial and cosmic neutrinos.
GRAIN is a vessel containing ~1 ton of liquid Argon (LAr) in which neutrinos can interact. The charged particles generated in these interactions move inside the LAr emmitting scintillation light, which is detected by SiPMs placed on the walls of the vessel. As already explained, the SiPMs are arranged in 76 cameras, which consist in 32x32 matrices.

# Running the script
In order to be able to run the simulation of the detector response, few steps are required:
- Own an account to be submit job on the Virtual Machine
- Have Pyhton3 installed on the VM together with the PyROOT module
- install the **drdf** package on the VM
- Install the script on the VM

## Account request

## Required softwares

### The drdf module

## Fast_resp installation

## Launching a production
This python program has 5 options and takes as input 3 parameters.
The submission comand therefore is

`python3 fast_resp.py <config_file> <input_ROOT_file> <output_drdf_file> -nc
-e <event_number> -i <idrun>`

where 
- `config_file`: contains some parameters for the DAQ simulation, such as the PDE and cross-talk probability for the SiPM sensors, togheter with their physical dimensions. The file name is *config.xml*.
- `input_ROOT_file`: is a file named *sensors.root*, which contains all the information about the photons propagating from the charged particles trajetories towards the sensors surface. In particular it provides the energy, arrival time and inpact coordinates of each photon.
- `output_drdf_file`: is usually a file named *response.drdf*. It is an image file in a custom-made format. The single response.drdf file contains the 2D plot of all the sensor matrices with the number of photons detected on each SiPM and the arrival time of the first one of them.
- `-nc` option: this options allows the user to retrive the total number of photons arrived on each SiPM without considering, for example, PDE or cross-talk.
- `-e` option: allows the user to specify the maximum number of event to be computed, if different from the number overall one.
- `-i` option: 

The input file obtained through the processing of a GEANT4 simulation of a neutrino interaction inside liquid Argon with other programs, which leads to the sensors.root file. Since they are not the result of my work I won't upload here the whole simulation chain scripts.

# HTCondor

### Submission on Personal Computer
In order to be able to submit this code on your PC, the following requirements are essential:
- Linux or WSL 
- Python3 
- PyROOT module 
- drdf module (go to the dedicated Section)
- a *sensor.root* input file (an example set is already provided)


  
### Submission on Virtual Machine

### Submission on HTCondor through bash script
An easier and more useful way to submit the detector response is using the bash script *launch_resp.sh*, which creates automatically the folders and allows t



