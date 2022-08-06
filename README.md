# Table of contents
- [Fast detector response](#fast-detector-response)
- [The physics case](#the-physics-case)
- [Running the script](#running-the-script)
  - [Account request](#account-request)
  - [Required softwares](#required-softwares)
    - [The drdf module](#the-drdf-module)
  - [Fast_resp installation](#fast_resp-installation)
  - [Launching a production](#launching-a-production)
    - [Submission on Virtual Machine](#submission-on-virtual-machine)
- [HTCondor](#htcondor)


# Fast detector response

The aim of this program is to simulate the Readout system of a detector composed by Silicon Photomultiplier (SiPM) sensors. They are arranged in 76 matrices (called cameras) of 32x32 sensors each, covering the internal walls of a vessel containing a scintillating material. Their scope is to detect the scintillation light produced by a charged particle moving inside the scintillating material. Using this program you can perform a calorimetric measurement, obtaining the energy of the incoming particle.

The program gives as output the distribution of photons on each camera, in a drdf file, which is a custom image format (more on this later).

# The physics case
The DUNE experiment is a long-baseline neutrino experiment which is under construction in the US between the Fermilab, where the neutrino beam will be generated, and hte Stanford Underground Research Facility in South Dakota.
The experiment will study neutrino oscillations trying to measure the $\delta_{cp}$ phase of the PMNS matrix and the neutrino mass ordering. It will also be able to detect cosmic neutrinos, providing important information about cosmic ray sources, useful for multimessenger astrophysics.

DUNE is composed by a Near Detector (ND) and a Far Detector (FD), consisting of a large TPC filled with liquid Argon. The ND has the scope of monitoring the neutrino beam just after its generation and is composed of three sub-detectors: GasAr-TPC, , and the SAND detector.

SAND in turn has three modules enclosed in a superconducting magnet: a Straw Tube Tracker, an electromagnetic calorimeter and GRAIN.

The GRAIN (GRanular Argon fot Interctions of Neutrinos) module, part of the SAND (System for on-Axis Neutrino Detection) detector of the DUNE experiment, a long-baseline experiment for the detection of artificial and cosmic neutrinos.
GRAIN is a vessel containing ~1 ton of liquid Argon (LAr) in which neutrinos can interact. The charged particles generated in these interactions move inside the LAr emmitting scintillation light, which is detected by SiPMs placed on the walls of the vessel. As already explained, the SiPMs are arranged in 76 cameras, which consist in 32x32 matrices.

# Running the script
It is possile to run the script both on a local device or on a Virtual Machine. 
If your intent is the submission on a local machine you can skip the following sections, going directly to [Launching a production](#launching-a-production).

However, to simulate a large number of events it is much more conveninet to rely on a virtual machine, which allows a faster execution time exploiting the possibility of running multiple events at the same time.

In order to be able to run the simulation of the detector response, few steps are required:
- Own an account to be submit job on the Virtual Machine
- Have Pyhton3 installed on the VM together with the PyROOT module
- install the *drdf* package on the VM
- Install the script on the VM

## Account request
Depending on which organization you belong to, different accouts could be allowed:
- A neutrino-01 account (look [here](https://www.cnaf.infn.it/en/users-faqs/) to read how to get one). This is needed to access the neutrino-01 CNAF machine. This is the machine from which the script will be executed and that will store all the output files. This account is mandatory to use fast_resp.
- 

## Required softwares
The only software which is not available publicly is the drdf package, necessary to build the output files. 
Installing this repository the user will get automaticly the `drdf.py` file. For the ones who have an account on *baltig* the same software is available [here](https://baltig.infn.it/dune/sand-optical/drdf).

### The drdf module


## Fast_resp installation
Login on the neutrino-01 machine. From a local terminal:
```
ssh <HTC_user>@bastion.cnaf.infn.it
ssh <HTC_user>@131.154.161.32
```
this should put you in the folder
```
/home/NEUTRINO/<HTC_user>
```

from here, clone this repository in the preferred location
```
git@github.com:chiappo98/fast_detector_Response.git  
```
--------------------->>>>>>>>>>>to verify

Before submitting a production pay attention to have installed python3, togheter with all the modules imported in `fast_resp.py`.

## Launching a production
`fast_resp.py` takes in input 3 parameters and has 3 additional options.
The submission comand therefore is
```
python3 fast_resp.py <config_file> <input_ROOT_file> <output_drdf_file> -nc
-e <event_number> -i <idrun>
```
where 
- `config_file`: contains some parameters for the DAQ simulation, such as the PDE and cross-talk probability for the SiPM sensors, togheter with their physical dimensions. The file name is *config.xml*.
- `input_ROOT_file`: is a file named *sensors.root*, which contains all the information about the photons propagating from the charged particles trajetories towards the sensors surface. In particular it provides the energy, arrival time and inpact coordinates of each photon.
- `output_drdf_file`: is usually a file named *response.drdf*. It is an image file in a custom-made format. The single response.drdf file contains the 2D plot of all the sensor matrices with the number of photons detected on each SiPM and the arrival time of the first one of them.
- `-nc` option: this options allows the user to retrive the total number of photons arrived on each SiPM without considering, for example, PDE or cross-talk.
- `-e` option: allows the user to specify the maximum number of event to be computed, if different from the number overall one.
- `-i` option: 

The input file obtained through the processing of a GEANT4 simulation of a neutrino interaction inside liquid Argon with other programs, which leads to the sensors.root file. Since they are not the result of my work I won't upload here the whole simulation chain scripts.

As already stressed, if the user's intent is run the response on his local device, the procedure described above its enough. If instead he wants to use a Virtual Machine the following section could be useful.

### Submission on Virtual Machine
Together with the fast response, in this repository the user can find also the `launch_resp.sh` bash script. It provides a fast and easy way to submit the job on the VM and retrive information on its status, creating also new folders to store the response output.

**NOTE: the bash script is set to work on the neutrino-01 machine. If you work on a different VM make sure to modify properly the submission and control commands. From now on I will mention only to the neutrino-01 machine, with the implicit reference to _your own_ virtual machine**

Once logged on neutrino-01 you can launch the detector response through the bash script with the following command
```
bash launch_resp.sh -i <INPUT_file_PATH> -f <OUTPUT_folder_PATH> -d <OUTPUT_folder_NAME> -e <MAX_event_NUMBER> -n <NUMBER_of_REPETITIONS>
```
There is also the possibility to run the simulation in backgroud, using the commad
```
nohup bash launch_resp.sh -i <INPUT_file_PATH> -f <OUTPUT_folder_PATH> -d <OUTPUT_folder_NAME> -e <MAX_event_NUMBER> -n <NUMBER_of_REPETITIONS> > out.log &
```

# HTCondor

### Submission on Personal Computer
In order to be able to submit this code on your PC, the following requirements are essential:
- Linux or WSL 
- Python3 
- PyROOT module 
- drdf module (go to the dedicated Section)
- a *sensor.root* input file (an example set is already provided)



### Submission on HTCondor through bash script
An easier and more useful way to submit the detector response is using the bash script *launch_resp.sh*, which creates automatically the folders and allows t



