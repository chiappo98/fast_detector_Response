# Table of contents
- [Fast detector response](#fast-detector-response)
- [The physics case](#the-physics-case)
- [Before starting](#before-starting)
  - [Account request](#account-request)
  - [Required softwares](#required-softwares)
    - [The drdf module](#the-drdf-module)
  - [Fast Response installation](#fast-response-installation)
  - [Download input files](#download-input-files)
- [Running fast_resp](#running-fast_resp)
- [Submission on batch system](#submission-on-batch-system)
  - [HTCondor](#htcondor)
  - [Launching a production](#launching-a-production)
    - [Input file](#input-file)
    - [Job size](#job-size)
    - [Production folder](#production-folder)
- [Output analysis](#output-analysis)

# Fast detector response

The aim of this program is to simulate the readout system of the GRAIN detector, a vessel filled with liquid Argon (LAr) and surrounded by Silicon Photomultiplier (SiPM) sensors. It is part of the DUNE experiment, devoted to neutrino detection. In GRAIN, SiPMs are arranged in 76 matrices (called cameras) of 32x32 sensors each, covering the internal walls of the vessel. Their scope is to detect the scintillation light produced by charged particles generated from neutrino interactions. 

The program gives in output the distribution of photons on each camera, and is able to compare the total number of detected photons with the energy deposited by charged particles.

# The physics case

The Deep Underground Neutrino Experiment (DUNE) is a long-baseline neutrino experiment which is under construction in the US between Fermilab, where the neutrino beam will be generated, and the Stanford Underground Research Facility in South Dakota.
The experiment will study neutrino oscillations trying to measure the $\delta_{cp}$ phase of the PMNS matrix and will try to discriminate neutrino mass ordering. It will also be able to detect cosmic neutrinos, providing important information about cosmic ray sources, useful for multimessenger astrophysics.

<p align = "center">
<img src="/images/dune.png" width="500" class="center"/>
</p>

DUNE is composed by a Near Detector (ND) and a Far Detector (FD), this latter consisting of a large TPC filled with liquid Argon. The ND has the scope of monitoring the neutrino beam just after its generation; it is composed of three sub-detectors: a GAr-TPC, a LAr-TPC, and the SAND detector.

<p align = "center">
<img src="/images/nearDetector.png" width="400" class="center"/>
</p>

SAND is divided into three modules enclosed in a superconducting magnet: a Straw Tube Tracker, an electromagnetic calorimeter and GRAIN.

<p align = "center">
<img src="/images/sand.png" width="500" class="center"/>
</p>

<p align = "center">
The SAND detector. On the left you can see the GRAIN module surrounded by the ECAL.
</p>

The GRanular Argon fot Interctions of Neutrinos (GRAIN) module is a vessel containing ~1 ton of liquid Argon in which neutrinos can interact. The charged particles generated in these interactions move inside LAr emmitting scintillation light, which is detected by SiPMs placed on the walls of the vessel. As already explained, the SiPMs are arranged in 76 cameras, which consist in 32x32 matrices.

<p align = "center">
<img src="/images/grainCam.png" width="300" class="center"/>
</p>

<p align = "center">
View of the GRAIN vessel, with SiPM cameras on its walls.
</p>

In order to be able to reconstruct the energy of a neutrino event in GRAIN, we should obtain a calibration coefficient to estimate the total deposited energy from the number of the detected photons.
This program makes a first step in this direction. Unfortunately the comparison of the energy of the event with the total number of photons gives only a rough estimation of the calibration coefficient. The number of photons which reach the SiPMs in fact depends on *where* the energy has been deposited inside the vessel: same events in different positions inside GRAIN generate a different number of photons.
In order to be more realistic the correct path should be the determination of different coefficients for different volume regions.

# Before starting

It is possible to run the simulation of the detector response both on a local device or on a remote machine. 
However, to simulate efficiently a large number of events it is much more convenient to rely, if possible, on distributed computing, which allows for a faster execution time exploiting the possibility of running multiple events at the same time. In particular I used the HTCondor batch system (more on this in section [HTCondor](#htcondor)).

In order to be able to run the simulation of the detector response, few steps are required:
- own an account to access a machine within the pool that may submit jobs, termed a submit machine
- have all the required softwares installed on the submit machine
- install the program executable and any needed input files for the fast detector response on the file system of the submit machine

## Account request

In order submit the detector response on HTCondor, an account to access the submit machine is needed. Working on the detector response I access via ssh the Tier-1 user interfaces (UI) connecting to *bastion.cnaf.infn.it*, the CNAF gateway. I use in particular the experiment dedicated UI called *neutrino-01* machine (16core/8GB ram), which CNAF kindly provided to the DUNE collaboration, to which I belong. The machine is reachable with ip 131.154.161.32 from *bastion.cnaf.infn.it*.

[Here](https://confluence.infn.it/pages/viewpage.action?pageId=40665299) you can find more information on INFN-CNAF Tier-1.

### WARNING
In the following sections I will always refer to job submission on the *neutrino-01* machine, which adopts the HTCondor batch system. However, users can obviously use different submit machines. Furthermore, if the batch system is different form HTCondor, the *launch_splitted_response.sh* shell script has to be modified to include the new submission command.

In *launch_splitted_response.sh*, lines 144-148 and 154, the user who it's not logged on neutrino-01 must check if the paths are sill valid or need to be changed.

## Required softwares

On the file system of the submit machine Pyhton3 has to be installed. Looking at the first lines of the py programs in this repository users can check the additional modules which are needed (in particular I underline the need for the PyROOT module).

The only software which is not a standard Python package is the drdf package, necessary to build the output files. 
Installing this repository the user will get automaticly the `drdf.py` file. For the ones who have access to GIT repositories at *baltig.infn.it* (you need to be registered as guest at INFN - Sezione di Bologna), the same software is available [here](https://baltig.infn.it/dune/sand-optical/drdf).

### The drdf module

*drdf*, which stands for 'Detector Response Data Format', is a custom image format created by Nicolò Tosi (INFN - Section of Bologna) in order to store efficiently a high number of images, from multiple events. From a single event in fact we obtain 2x76 images, since 76 is the number of cameras in the GRAIN detector, and for each of them we store 2 images of size 32x32 pixels.
The two images store respectively the amplitude (number of photons detected) of each pixel and the arrival time of the first photon, again on each pixel.
A drdf file stores images labelled with their *uuid*, *event*-number, *camera*-number; the information contained in every camera can be retrived calling each specific pixel through its number (from 0 to 1023).

In the *drdf_test* folder the user can find two useful tutorials for reading and writing a drdf file, from which it is possible to better understand the structure of the file.

## Fast response installation

Connect first to bastion.cnaf.infn.it, the CNAF gateway, and then login on the neutrino-01 machine. From a local terminal:
```
ssh <HTC_user>@bastion.cnaf.infn.it
ssh <HTC_user>@131.154.161.32
```
this should put you in the folder
```
/home/NEUTRINO/<HTC_user>
```
from here, clone this repository in the preferred location **inside** `/storage/gpfs_data/neutrino/SAND-LAr/`
```  
git clone https://github.com/chiappo98/fast_detector_Response.git
```

The fact that a the installation of the repository must be done inside a specific folder is due to the existence of a file system shared by the submit machine and the execute machine.

At this point, the user may choose between two possibilities:
- Execute *fast_resp.py* on neutrino-01.
- Execute *splitted_resp.py*  submitting one or more jobs to HTCondor.

In the first case the user may simply follow instructions provided in section [Running fast_resp](#running-fast-resp). 

In order to work with HTCondor (exploiting its adavntages) instead, `splitted_fast_resp.py` and `launch_splitted_response.sh` are provided to the user. They represent a fast and easy way to submit jobs on the batch system and retrive information on their status, creating at the same time new folders to store the response output.

In both cases the output of the detector response will be the same, even if the two scripts are implemented in different ways.

## Download input files

I provide to the user some files which can be used as input files for the detector response simulation. They are called *sensors.root* and contains information about the photons generated from a neutrino interaction which reach the SiPMs.
In particular I provide files containing: 
* 1 event
* 3 events
* 10 events
* 100 events

With 'event' I mean a single neutrino interaction happened inside the GRAIN volume, which gives rise to scintillation photons from charged particles propagation. 
This means that analysing the second file the user will simulate three different neutrino events, with the interaction vertex located randomly inside the LAr volume.

It's important to konw how many events a *sensors.root* file contains, in order to set the correct parameters for the simulation.

Since they are quite heavy files, they are stored on my personal Google Drive. I shared them so that using the commands below everyone will be able to download them directly into the preferre folder on neutrino-01.

So, first of all, create a dedicated folder for the file, if possible in the same location of the cloned repository. I suggest to create an `input_file` directory with dedicated folders inside
```
mkdir /storage/gpfs_data/neutrino/SAND-LAr/../input_file
mkdir /storage/gpfs_data/neutrino/SAND-LAr/../input_file/3_events
```
At this point, navigate to the *N_events* folder, and use the following commands:
* 1 event (62 MB)
```
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1mhChJm1__PEa0DA_aEdEBrrcdMYDSWjK' -O sensors.root
```
* 3 events (249 MB)
```
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1lganVEn5Y7uXqpNkoSPi2tcJ88k84JsD' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1lganVEn5Y7uXqpNkoSPi2tcJ88k84JsD" -O sensors.root && rm -rf /tmp/cookies.txt
```
* 10 events (509 MB)
```
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1KhQUk276fSw0U2uzAGRSEt_CuF6kdPD8' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1KhQUk276fSw0U2uzAGRSEt_CuF6kdPD8" -O sensors.root && rm -rf /tmp/cookies.txt
```
* 100 events (4035 MB)
```
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1RSMwA6xBTjngQktb5yZ-7d5VBVouJboU' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1RSMwA6xBTjngQktb5yZ-7d5VBVouJboU" -O sensors.root && rm -rf /tmp/cookies.txt
```

There is one last file to download: *1000_numu_in_GRAIN.edep_sim.root*. It contains the result of the particles interaction simulation inside GRAIN. This is the file from which the *sensors.root* files provided above are created (with dedicated software).

[Edepsim](https://github.com/ClarkMcGrew/edep-sim) output format can be found [here](https://indico.cern.ch/event/687511/contributions/2822503/attachments/1574001/2484800/Edep-sim_output.pdf#search=edep-sim%20output). 
Among all the information stored in this file, we are interested in the energy deposit. During the [Output analysis](#output-analysis) in fact we compare the number of detected photons wrt the energy deposited by charged particles.

As done before, I suggest to create a dedicated folder 
```
mkdir /storage/gpfs_data/neutrino/SAND-LAr/../input_file/edepsimFile
```

The download is started with the following command
```
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1P21O8OJ-OuY4Cc_FH7n7S7VILYBPA2ZP' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1P21O8OJ-OuY4Cc_FH7n7S7VILYBPA2ZP" -O 1000_numu_in_GRAIN.edep_sim.root && rm -rf /tmp/cookies.txt
```

# Running fast_resp

In order to run the detector response on the neutrino-01 machine, *fast_resp.py* must be used. It takes in input 3 parameters and has 4 additional options.
The submission comand therefore is
```
python3 fast_resp.py <config_file> <input_ROOT_file> <output_drdf_file> -nc -e <event_number> -s <start_event> -i <idrun>
```
where 
- `config_file`: contains some parameters for the DAQ simulation, such as the PDE and cross-talk probability for the SiPM sensors, togheter with their physical dimensions. The file name is *config.xml*.
- `input_ROOT_file`: a file named *sensors.root*, which contains all the information about the photons propagating from the charged particles trajetories towards the sensors surface. In particular it provides the energy, arrival time and inpact coordinates of each photon.
- `output_drdf_file`: a file named *response.drdf*. It is an image file in a custom-made format. The single response.drdf file contains the 2D plot of all the sensor matrices with the number of photons detected on each SiPM and the arrival time of the first one of them.
- `-nc` option: this options allows the user to retrive the total number of photons arrived on each SiPM without considering, for example, PDE or cross-talk.
- `-e` option: allows the user to specify the number of event to be computed, if different from the total one.
- `-s` option: allows the user to specify the starting event, if different from 0. To be used *only* if the number of event is *smaller* than the total one.
- `-i` option: run identifier (UUID)

The input file is obtained through the processing, with other sofwares, of the GEANT4 simulation of a neutrino interaction inside liquid Argon. This leads to the sensors.root file. Since they are not the result of my work I won't upload here the softwares whole simulation chain.

# Submission on batch system

Through CNAF the user can get access to the INFN computing centre, exploiting the use of Grid technology. It is in this constest that the creation of a fast detector response makes sense, since the term 'fast' derives from the possibility to run many simulations in parallel. HTCondor helps to accomplish this task, since it is a specialized batch system for managing compute-intensive jobs, providing a queuing mechanism, scheduling policy, priority scheme, and resource classifications. 

## HTCondor

The power of HTCondor batch system is the possibility to submit jobs in parallel. In our case for example, one may submit *N* jobs to HTCondor, running *n*-times the fast response on the same set of events or, (and this is what *launch_splitted_response.sh* does) *N*-times the fast response on *N* different sets of events. 

The usage of HTCondor on *neutrino-01* for the fast response allows to split the events we have to process into subsamples which can run simultaneously, shortening the execution time.

In order to submit a job on HTCondor we have to prepare two files:
- `splitted_fast_resp.sh` : contains the command to launch the python script *splitted_fast_resp.py* and the PATH to the needed packages.
- `splitted_fast_resp.sub` : contains the instructions to run jobs on HTCondor, such as the number of jobs to be submitted, the name of the executable (*splitted_fast_resp.sh*), the names of log, err, and out files for each job, form which you can retrive informations on the execution of the job and on eventual errors.

The CNAF Tier-1 infrastructure provides a submit node for submission from local UI: *sn-02.cr.cnaf.infn.it*.
To submit jobs locally, i.e. from CNAF UI, use the following command:
```
condor_submit -name sn-02.cr.cnaf.infn.it -spool <path_to_fast_resp.sub>
```
whereas, to see information about a single job use
```
condor_q -nobatch -af JobStatus -name sn-02.cr.cnaf.infn.it $JOB_ID
```
In case of parallel job submission to have information on a particular job we have to specify also its number *e.g.* 0,1,2,...,n.

All this sequence of job submission and monitor is embedded inside *launch_splitted_response.sh*.

For more information about HTCondor read [HTC - Job Submission](https://confluence.infn.it/display/TD/9+-+Job+submission) and the [HTC homepage](https://research.cs.wisc.edu/htcondor/).

## Splitted fast response 

The fast response is coded inside *splitted_fast_resp.py*. This program works in a very similar way wrt *fast_resp.py*, except for the fact that it is optimised for parallel submission on HTCondor and that the input parameters are given through a *config.txt* file.

Therefore the script will be executed with the command
```
python3 splitted_fast_resp.py <config_file>
```
The configuration file has the following structure:
```makefile
<configfile>      #configuration .xml file
<fname>           #simulation output .root file
<wfile>           #output .drdf file
<nocut>           #count total number of photons  (True or False)
<jobNumber>       #number of current job
<jobSize>         #size of submitted job 
<start_evn>       #staring event (if not 0)
<idrun>           #(True or False) run identifier (UUID)   ---> if True, read also line 7
<idrun>           #idrun 
```
Here, unlike in *fast_resp.py*, the `-e` option is substituted by `<jobNumber>` and `<jobSize>`: the number of the current job (among the *N* submitted) and its size (in 'number of events'). In this way the program can extract from *sensors.root* the events which has to process in that particular job, computing the range $(start, stop)$ where `start = start_evn + jobNumber*jobSize` and `stop = start_evn + (jobNumber + 1)*jobSize`.

The output file of a single job is named *response_n.drdf*, where *N* is the number of the particular job.

These configuration parameters are written in the configuration file by *launch_splitted_response.sh*, without any space or any other sign. The script further copy and modifies the original *config.txt* into *N* configuration files (named *config_N.txt*), necessary for the submission of *N* parallel jobs on HTCondor.

## Launching a production

Once logged on neutrino-01 you can launch the detector response through the shell script with the following command
```
bash launch_splitted_response.sh -c <RESPONSE_CONFIG>
```
where *<RESPONSE_CONFIG>* is a *txt* file (different from the one used for the splitted fast response) containing all the configuration parameters for starting the production. 
The file must be compiled by the user according to the followig structure:
```makefile
inputFile = /path/to/input/file
ProductionFolder = /path/to/output/folder
eventNumber = <number>
jobSize = <number>
startingEvent = <number>
responseConfig = /path/to/config/xml/file
edepFile = /path/to/config/edepsim/file
FastAnalysis = <yes/no>
PlotCameras = <yes/no>
```
* `inputFile` must be an absolute path to *sensors.root*.
* `ProductionFolder` must be an absolute path to the output folder (output folder not included).
* `eventNumber` must be the number of events to simulate in the detector Response simulation.
* `jobSize` is used to set the number of events to simulate in every job (and the number of submitted jobs as a consequence).
* `startingEvent` is used to choose the starting entry of the file.
* `responseConfig` is used to choose the configuration file for the detector response.
* `edepFile` must be an absolute path to *1000_numu_in_GRAIN.edep_sim.root*.
* `FastAnalysis` is used to analyse the detector response output. More on this below.
* `PlotCameras` is used to plot the photon distribution of each camera.

Please note that:
* the order of the parameters can be changed
* **there must be** a space before and after the =
* there should not be blank lines between the parameters (to be confirmed)

There is also the possibility to run the simulation in backgroud, using the commad
```
nohup bash launch_splitted_response.sh -c <RESPONSE_CONFIG> > out.log &
```
To check how the job proceeds just look inside the *out.log* file.

**ATTENTION:** I stress again that in order to launch succesfully a production, input files and scripts have to be copied to a folder somewhere inside `/storage/gpfs_data/neutrino/SAND-LAr/`, the shared folder accessible by HTCondor.

### Configuration file

This repository contains a *configs* folder: it must be used to store the various configuration files. Each *config.txt* must be put inside a new folder with a specific name. That name will be also the name of the production directory which will be created to store the output of the simulation.

### Input file

This is the file used as input by the simulation. The path to this file must be specified in the config file as described above.

For *sensors.root* files the default location should be somewhere inside
```
/storage/gpfs_data/neutrino/SAND-LAr/
```

### Job size

The jobSize parameter is used to define the number of events to be simulated in each job and, consequentially, to submit more jobs for the OptMen simulation. 

The number of jobs is computed as `eventNumber/jobSize`.

For each job, different output files will be generated. The name of the files will be followed by the number of the job, *i.e. response_10.drdf*.

### Production folder

The output folder structure is the following:
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
As already said, the *response_N.drdf* files are the output of the *N* submitted jobs. At this point, the `merge.py` script allows to unify them into a single *response.drdf* file, which is more easy to analyse. 

The script is executed by the shell script, when all jobs are completed.

# Output analysis
The analysis of *response.drdf* can be done using `fast_analysis.py`.
This program is able to read the drdf file showing the results of the simulations. In particular we plot the energy deposited by charged particles wrt the number of photons detected by SiPMs. This allows to compute a calibration coefficient form which, measuring the number of photons detected we can obtain the energy deposited inside the LAr volume.

The energy deposit is read from *1000_numu_in_GRAIN.edep_sim.root*, paying attention to select the same events that has been simulated in the detector response.

<p align = "center">
<img src="/images/cam70.png" width="300" class="center"/>
</p>   

<p align = "center">
Example of a SiPM camera plotted from the drdf file. The amplitude of each pixel corresponds to the number of photons detected.
</p> 

Another option of *fast_analysis.py* is the possibility to plot the distribution of photons on each camera, for all the simulated events. This is only an option, disabled as default, since it takes a large amount of time. However, once enabled, the images of the 76 cameras of the *N*-th event will be saved in the *event_N* folder, inside *camera_folder*.

This is the structure of the *output_analysis* folder, created inside the production directory.
```bash
- output_analysis                           
    ├─ amplitudeVenergy.png              # amplitude vs energy 
    ├─ energyVamplitude.png              # energy vs amplitude 
    │
    └─ cameras_folder
        ├─ event0                 # folder with cameras from event 0 
        │    ├─ cam1.png          # photon distribution on camera 1
        │    ├─ cam2.png          # photon distribution on camera 2
        │    ├─ cam3.png          # photon distribution on camera 3        
        │    └─ ...
        │
        ├─ event1                 # folder with cameras from event 1
        ├─ event2                 # folder with cameras from event 2
        └─ ...     
```

