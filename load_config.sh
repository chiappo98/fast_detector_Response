#!/bin/bash
while getopts "c:" o; do
  case "$o" in
    c)  CONFIG=${OPTARG}; CONFIG_FLAG=true;;
  esac
done

if [ ! $CONFIG_FLAG ]; then
  echo "No config file defined!"
  exit 2
fi

if [ ! -f $CONFIG ]; then
  echo "$CONFIG not found! Stopping the script."
  exit 2
fi

echo "========================================================"
echo "             Loading configuration file\e[0m."
echo "========================================================"

INPUTFILE=$(awk -F "inputFile =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
INPUTFILE=$(echo $INPUTFILE | sed "s/\\r\\n//g")
echo "Input file: \e[4;96m${INPUTFILE}\e[0m"

SCRIPT_PATH=$(awk -F "ProductionPath =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
SCRIPT_PATH=$(echo $SCRIPT_PATH | sed "s/\\r\\n//g")
echo "ProductionPath: \e[4;96m${SCRIPT_PATH}\e[0m"

NEW_DIR=$(awk -F "new_Dir_Name =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
NEW_DIR=$(echo $NEW_DIR | sed "s/\\r\\n//g")
echo "new_Dir_Name: \e[4;96m${NEW_DIR}\e[0m"

EVENT_NUMBER=$(awk -F "eventNumber =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
EVENT_NUMBER=$(echo $EVENT_NUMBER | sed "s/\\r\\n//g")
echo "Event number: \e[4;96m${EVENT_NUMBER}\e[0m"

JOB_SIZE=$(awk -F "jobSize =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
#JOB_SIZE=$(echo $JOB_SIZE | sed "s/\\r\\n//g")
echo "Job size: \e[4;96m${JOB_SIZE}\e[0m"

STARTING_EVENT=$(awk -F "startingEvent =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
STARTING_EVENT=$(echo $STARTING_EVENT | sed "s/\\r\\n//g")
echo "Starting Event: \e[4;96m${STARTING_EVENT}\e[0m"

RESPONSE_CONFIG=$(awk -F "responseConfig =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
RESPONSE_CONFIG=$(echo $RESPONSE_CONFIG| sed "s/\\r\\n//g")
echo "Response config: \e[4;96m${RESPONSE_CONFIG}\e[0m"

FAST_ANALYSIS=$(awk -F "FastAnalysis =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
FAST_ANALYSIS=$(echo $FAST_ANALYSIS | sed "s/\\r\\n//g")
echo "FastAnalysis: \e[4;96m${FAST_ANALYSIS}\e[0m"

PLOT_CAMERAS=$(awk -F "PlotCameras =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
PLOT_CAMERAS=$(echo $PLOT_CAMERAS | sed "s/\\r\\n//g")
echo "PlotCameras: \e[4;96m${PLOT_CAMERAS}\e[0m"

SELF=$(realpath $0)
REALPATH=$(dirname $(realpath ${CONFIG})) #--relative-to $(dirname ${SELF})/configs))   #----->>>>need / <<<--------
#SCRIPT_PATH=$REALPATH
#SCRIPT_FOLDER=$REALPATH/${NEW_DIR}
#OUTPUT_FOLDER=$SCRIPT_FOLDER/output
#EXECUTABLE=$REALPATH/drdf.py
#OUTPUT_FOLDER=$SCRIPT_FOLDER/log
#TMP_LOG=${LOGS_FOLDER}/tmp_log
#JOBNUMBER=$(( (${EVENT_NUMBER} + ${JOB_SIZE} - 1) / ${JOB_SIZE} ))
#-----------------------------------------------------------------------------------------------------------------------------------------
SCRIPT_FOLDER=$SCRIPT_PATH/${NEW_DIR}
#SCRIPT_PATH=/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-GRAIN-CALORIMETRY/scratch/fastCalo_submission/
OUTPUT_FOLDER=${SCRIPT_FOLDER}/output
#CONFIG=/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-GRAIN-CALORIMETRY/scratch/fastCalo_submission/config.xml
EXECUTABLE=${SCRIPT_PATH}/drdf.py
LOGS_FOLDER=${SCRIPT_FOLDER}/log
TMP_LOG=${LOGS_FOLDER}/tmp_log
JOBNUMBER=$(( (${EVENT_NUMBER} + ${JOB_SIZE} - 1) / ${JOB_SIZE} ))

echo "========================================================"
echo "                Configuration loaded.\e[0m"
echo "========================================================"
