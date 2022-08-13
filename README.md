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
In order submit the detector response on a Virtul Machine, an account is needed. Working on the detector response I access via ssh the Tier-1 user interfaces (UI) connecting to *bastion.cnaf.infn.it*, the CNAF gateway, using in particular the experiment dedicated UI called *neutrino-01*, which is devoted to the DUNE collaboration, to which I belong to.

[Here](https://confluence.infn.it/pages/viewpage.action?pageId=40665299) you can find more information on the INFN-CNAF Tier-1.

In the following sections I will always refer to job submission on the *neutrino-01* VM. However, the user is free to adapt the programs, and in particular the bash script *launch_splitted_response.sh*, to the VM they have access to.

The neutrino-01 machine adopts the HTCondor batch system (more on this in section [HTCondor](#htcondor)).

## Required softwares
The only software which is not available publicly is the drdf package, necessary to build the output files. 
Installing this repository the user will get automaticly the `drdf.py` file. For the ones who have access to GIT repositories at *baltig.infn.it* (you need to be registered as guest at INFN - Sezione di Bologna), the same software is available [here](https://baltig.infn.it/dune/sand-optical/drdf).

### The drdf module


## Fast_resp installation
Connect first to bastion.cnaf.infn.it, the CNAF gateway, and then login on the neutrino-01 machine. From a local terminal:
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
*fast_resp.py* takes in input 3 parameters and has 4 additional options.
The submission comand therefore is
```
python3 fast_resp.py <config_file> <input_ROOT_file> <output_drdf_file> -nc -e <event_number> -s <start_event> -i <idrun>
```
where 
- `config_file`: contains some parameters for the DAQ simulation, such as the PDE and cross-talk probability for the SiPM sensors, togheter with their physical dimensions. The file name is *config.xml*.
- `input_ROOT_file`: is a file named *sensors.root*, which contains all the information about the photons propagating from the charged particles trajetories towards the sensors surface. In particular it provides the energy, arrival time and inpact coordinates of each photon.
- `output_drdf_file`: is usually a file named *response.drdf*. It is an image file in a custom-made format. The single response.drdf file contains the 2D plot of all the sensor matrices with the number of photons detected on each SiPM and the arrival time of the first one of them.
- `-nc` option: this options allows the user to retrive the total number of photons arrived on each SiPM without considering, for example, PDE or cross-talk.
- `-e` option: allows the user to specify the number of event to be computed, if different from the total one.
- `-s` option: allows the user to specify the starting event, if different from 0. To be used *only* if the number of event is *smaller* than the total one.
- `-i` option: run identifier (UUID)

The input file obtained through the processing of a GEANT4 simulation of a neutrino interaction inside liquid Argon with other programs, which leads to the sensors.root file. Since they are not the result of my work I won't upload here the whole simulation chain scripts.

As already stressed, if the user's intent is run the response on his local device, the procedure described above its enough. If instead he wants to use a Virtual Machine the following section could be useful.

### Submission on Virtual Machine
In order to submit the fast response on a VM, `splitted_fast_resp.py` and `launch_splitted_response.sh` are provided to the user. They represent a fast and easy way to submit the job on the VM and retrive information on its status, creating also new folders to store the response output.
The power of HTCondor bash system (have I introduced it???????????????) is the possibility to submit jobs in parallel, so that one can run *n*-times the same program (process n times the same events) through *n* parallel jobs, or .....

The usage of HTCondor on *neutrino-01* for the fast response allows to split the events we have to process into subsamples which can run simultaneously

The fast response is coded inside *splitted_fast_resp.py*. This program works in a very similar way wrt *fast_resp.py*, except for the fact that it is optimised for parallel submission on HTCondor and that the input parameters are given through a *config.txt* file.

Starting from the configuration file, it has the following structure:
```
<configfile>      #configuration .xml file
<fname>           #simulation output .root file
<wfile>           #output .img file
<nocut>           #count total number of photons  (True or False)
<jobNumber>       #number of submitted job from bash script
<jobSize>         #size of submitted job from bash script
<start_evn>       #staring event (if not 0)
<idrun>           #(True or False) run identifier (UUID)   ---> if True, read also line 7
<idrun>           #idrun 
```
The parameters are written in the config file by the bash script, without any space or any other sign. *launch_splitted_response.sh* further copy and modifies the original *config.txt* into *#n* configuration files (named *config_n.txt*), necessary for the submission of *#n* parallel jobs on HTCondor.

Once logged on neutrino-01 (same procedure applied in [Fast_resp installation](#fast_resp-installation)) you can launch the detector response through the bash script with the following command
```
bash launch_splitted_response.sh -i <INPUT_file_PATH> -f <OUTPUT_folder_PATH> -d <OUTPUT_folder_NAME> -e <MAX_event_NUMBER> -s <JOB_SIZE> -x <STARTING_EVENT>
```
where
- `-e` is the same option given in the fast_resp.py, to specify the maximum number of events to be analysed.
- `-s` determines the size of the job, *i.e.* the number of events processed in each job.
- `-x` gives the possibility to specify the starting event, if the number of events given is *less* than the total one.

Notice that when specifying the *output_folder_path* you don't have to insert the name of the output folder, which is instead to be specified in the following argument.

There is also the possibility to run the simulation in backgroud, using the commad
```
nohup bash launch_splitted_response.sh -i <INPUT_file_PATH> -f <OUTPUT_folder_PATH> -d <OUTPUT_folder_NAME> -e <MAX_event_NUMBER> -s <JOB_SIZE> -x <STARTING_EVENT> > out.log &
```
To check how the job proceeds just look inside the *out.log* file.

The output structure is as follows:
```bash
- outputFolder                            # root folder of the output files
    ├─ splitted_fast_resp.sub             # fast_resp submission file
    ├─ splitted_fast_resp.sh              # fast_resp submission file
    ├─ config.txt
    │   
    ├─ log  
    │   ├─ tmp_log                        # log of submitted jobs
    │   ├─ time.log                       # contains the timing of the submitted jobs
    │   ├─ splitted_fast_resp.log         # log of fast response 
    │   ├─ splitted_fast_resp.err         # err of fast response 
    │   ├─ splitted_fast_resp.out         # out of fast response 
    │   ├─ job_log
    │   │   ├─ job_0.log          #log from submission of job 0
    │   │   ├─ job_1.log          #log from submission of job 1
    │   │   └─ ...
    │   └─ job_err
    │       ├─ job_0.err          #err from submission of job 0
    │       ├─ job_1.err          #err from submission of job 1
    │       └─ ...
    │
    ├─ many_configs
    │   ├─ config_0.txt           #configuration file for fast response of event 0
    │   ├─ config_1.txt           #configuration file for fast response of event 1  
    │   └─ ...
    │
    └─ output
        ├─ response.drdf          # pixel signal output in drdf format of all events
        ├─ response_0.drdf        # pixel signal output in drdf format of event 0
        ├─ response_1.drdf        # pixel signal output in drdf format of event 1
        └─ ... 
```

### HTCondor
For HTCondor to run a job, it must be given details such as the names and location of the executable and all needed input files. These details are specified in the submit description file, in this case `fast_resp.sh`. 

To submit the job, we need also to specify all the details such as the names and location of the executable and all needed input files creating a submit description file `fast_resp.sub`.

The CNAF Tier-1 infrastructure provides a submit node for submission from local UI: *sn-02.cr.cnaf.infn.it*.
To submit jobs locally, i.e. from CNAF UI, use the following command:
```
condor_submit -name sn-02.cr.cnaf.infn.it -spool <path_to_fast_resp.sub>
```
whereas, to see information about a single job use
```
condor_q -nobatch -af JobStatus -name sn-02.cr.cnaf.infn.it $JOB_ID
```
All this sequence of job submission and monitor is embedded inside *launch_splitted_response.sh*.

For more information look at [HTC - Job Submission](https://confluence.infn.it/display/TD/9+-+Job+submission).

### Submission on Personal Computer
In order to be able to submit this code on your PC, the following requirements are essential:
- Linux or WSL 
- Python3 
- PyROOT module 
- drdf module (go to the dedicated Section)
- a *sensor.root* input file (an example set is already provided)
