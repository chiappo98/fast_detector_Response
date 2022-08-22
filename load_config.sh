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
echo "             Loading configuration file."
echo "========================================================"

INPUTFILE=$(awk -F "inputFile =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
INPUTFILE=$(echo $INPUTFILE | sed "s/\\r\\n//g")
echo "Input file: ${INPUTFILE}"

SCRIPT_PATH=$(awk -F "ProductionPath =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
SCRIPT_PATH=$(echo $SCRIPT_PATH | sed "s/\\r\\n//g")
echo "ProductionPath: ${SCRIPT_PATH}"

NEW_DIR=$(awk -F "new_Dir_Name =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
NEW_DIR=$(echo $NEW_DIR | sed "s/\\r\\n//g")
echo "new_Dir_Name: ${NEW_DIR}"

EVENT_NUMBER=$(awk -F "eventNumber =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
EVENT_NUMBER=$(echo $EVENT_NUMBER | sed "s/\\r\\n//g")
echo "Event number: ${EVENT_NUMBER}"

JOB_SIZE=$(awk -F "jobSize =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
#JOB_SIZE=$(echo $JOB_SIZE | sed "s/\\r\\n//g")
echo "Job size: ${JOB_SIZE}"

STARTING_EVENT=$(awk -F "startingEvent =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
STARTING_EVENT=$(echo $STARTING_EVENT | sed "s/\\r\\n//g")
echo "Starting Event: ${STARTING_EVENT}"

RESPONSE_CONFIG=$(awk -F "responseConfig =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
RESPONSE_CONFIG=$(echo $RESPONSE_CONFIG| sed "s/\\r\\n//g")
echo "Response config:${RESPONSE_CONFIG}"

FAST_ANALYSIS=$(awk -F "FastAnalysis =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
FAST_ANALYSIS=$(echo $FAST_ANALYSIS | sed "s/\\r\\n//g")
echo "FastAnalysis: ${FAST_ANALYSIS}"

PLOT_CAMERAS=$(awk -F "PlotCameras =" '{if($2 != "")print $2;if($2 != "") exit;}' "${CONFIG}")
PLOT_CAMERAS=$(echo $PLOT_CAMERAS | sed "s/\\r\\n//g")
echo "PlotCameras: ${PLOT_CAMERAS}"

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
echo "                Configuration loaded."
echo "========================================================"
