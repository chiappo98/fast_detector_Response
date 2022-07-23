# fast_detector_Response

The aim of this program is to simulate the Readout system of the GRAIN (GRanular Argon fot Interctions of Neutrinos) module, part of the SAND (System for on-Axis Neutrino Detection) detector of the DUNE experiment, a long-baseline experiment for the detection of artificial and cosmic neutrinos.
GRAIN is a vessel containing ~1 ton of liquid Argon (LAr) in which neutrinos can interact. The charged particles generated in these interactions move inside the LAr emmitting scintillation light, which is detected by SiPMs placed on the walls of the vessel.

The SiPMs are arranged in 76 cameras, which consist in 32x32 matrices.
The fast_resp.py simulate the detection of scintillation photons giving as output the number of photons arrived at each sensor, in a drdf format (more on this later).

## The physics case
The DUNE experiment is a long-baseline neutrino experiment which is under construction in the US between the Fermilab, where the neutrino beam will be generated, and hte Stanford Underground Research Facility in South Dakota.
The experiment will study neutrino oscillations trying to measure the $\delta_{cp}$ phase of the PMNS matrix and the neutrino mass ordering. It will also be able to detect cosmic neutrinos, providing important information about cosmic ray sources, useful for multimessenger astrophysics.

DUNE is composed by a Near Detector (ND) and a Far Detector (FD), consisting of a large TPC filled with liquid Argon. The ND has the scope of monitoring the neutrino beam just after its generation and is composed of three sub-detectors: GasAr-TPC, , and the SAND detector.

SAND in turn has three modules enclosed in a superconducting magnet: a Straw Tube Tracker, an electromagnetic calorimeter and GRAIN.

## fast_resp.py - how it works
This python program has 5 options and takes as input 3 parameters.
The submission comand therefore is

>python3 fast_resp.py 

### Submission through bash script
An easier and more useful way to submit the detector response is using the bash script *launch_resp.sh*, which creates automatically the folders and allows t

## The drdf module

