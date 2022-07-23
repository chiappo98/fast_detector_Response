#!/bin/bash
while getopts "i:d:n:" o; do
  case "$o" in
    i)  INPUT=${OPTARG};;
    d)  NEW_DIR=${OPTARG} ;;
    n)  REP_NUM=${OPTARG} ;;
  esac
done
##NEW_DIR=test2_dir
##INPUT=/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-OPTICALSIM-PROD/GRAIN/calorimetry/GPC_prod/GENIE_V2/test_1.0.1/intermediate/inter_996/sensors_996.root 
SCRIPT_FOLDER=/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-GRAIN-CALORIMETRY/scratch/fastCalo_submission/${NEW_DIR}
SCRIPT_PATH=/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-GRAIN-CALORIMETRY/scratch/fastCalo_submission/
OUTPUT_FOLDER=/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-GRAIN-CALORIMETRY/scratch/fastCalo_submission/${NEW_DIR}/output
CONFIG=/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-GRAIN-CALORIMETRY/scratch/fastCalo_submission/config.xml
EXECUTABLE=/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-GRAIN-CALORIMETRY/scratch/fastCalo_submission/drdf.py
LOGS_FOLDER=/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-GRAIN-CALORIMETRY/scratch/fastCalo_submission/${NEW_DIR}/log
TMP_LOG=$LOGS_FOLDER/tmp_log

function setup_prod_dir() {
  mkdir $SCRIPT_FOLDER
  mkdir $LOGS_FOLDER
  mkdir $OUTPUT_FOLDER
  if [[ ! -d "/home/NEUTRINO/chiappon/calorimetry/${NEW_DIR}" ]]; then
    mkdir -p /home/NEUTRINO/chiappon/calorimetry/${NEW_DIR}
  fi
}

function check_errors() {
  STATUS="$?"
  if [[ $STATUS != "0" ]]; then
    echo "$?"
    echo "this error is occuring, stopping the script"
    exit 2
  fi
}

function check_condor() {
  JOB_ID=${1}
  N=${2}
  TIME=15
  while true
  do
    COMPLETED=0
    IDLE=0
    RUNNING=0
    HOLD=0
    UNKOWN=0
    sleep $TIME

    for ((i=0;i<N;i++)); do
      JOB_STATUS=$(condor_q -nobatch -af JobStatus -name sn-02.cr.cnaf.infn.it $JOB_ID.$i)

      if [[ $JOB_STATUS == "4" ]]; then
        ((COMPLETED++))
      elif [[ $JOB_STATUS == "1" ]]; then 
#        .log 7 "Job $i is IDLE."
        ((IDLE++))
      elif [[ $JOB_STATUS == "2" ]]; then 
#        .log 7 "Job $i is RUNNING."
        ((RUNNING++))
      elif [[ $JOB_STATUS == "5" ]]; then
#        .log 7 "Job $i is HOLD."
        ((HOLD++))
      else 
#        .log 7 "Job $i is in status $JOB_STATUS."
        ((UNKOWN++))
      fi
    done

    echo "Running $RUNNING, idle $IDLE, hold $HOLD, completed $COMPLETED." #>> "$LOGS_FOLDER/calorimetry_response.log"
    
    if [[ $COMPLETED == $N ]]; then
     echo "$COLOR All jobs completed." #>> "$LOGS_FOLDER/calorimetry_response.log"
	    condor_transfer_data -name sn-02.cr.cnaf.infn.it $JOB_ID
         
      condor_q -name sn-02.cr.cnaf.infn.it $JOB_ID -af ExitCode > $TMP_LOG
      sed -i '/0/d' $TMP_LOG
      if [ -s $TMP_LOG ]; then
        echo "At least one code error is not 0. Stopping the script." #>> "$LOGS_FOLDER/calorimetry_response.log"
        exit 2
      fi   
            
      true
	    return
    elif [[ $RUNNING -eq 0 ]] && [[ $IDLE -eq 0 ]] && [[ $(( COMPLETED + HOLD )) == $N ]]; then
      echo "All jobs completed, some are hold." #>> "$LOGS_FOLDER/calorimetry_response.log"
      condor_transfer_data -name sn-02.cr.cnaf.infn.it $JOB_ID
      
      condor_q -name sn-02.cr.cnaf.infn.it $JOB_ID -af ExitCode > $TMP_LOG
      sed -i '/0/d' $TMP_LOG
      if [ -s $TMP_LOG ]; then
        echo "At least one code error is not 0. Stopping the script." #>> "$LOGS_FOLDER/calorimetry_response.log"
        exit 2
      fi
      
      true
	    return
    elif [[ $UNKOWN > 0 ]]; then
      echo "Some jobs are in an unkown state." #>> "$LOGS_FOLDER/calorimetry_response.log"
      false
      return
    fi
    
  done
}

echo "running fastCalo with inputs: ${INPUT} ${NEW_DIR} ${REP_NUM}"
echo "Setting up production directory at $SCRIPT_FOLDER"
setup_prod_dir
check_errors

#fastCalo response
echo "Starting fastCalo response" #>> "$LOGS_FOLDER/calorimetry_response.log"
touch $SCRIPT_FOLDER/fastCalo.sh
> $SCRIPT_FOLDER/fastCalo.sh
echo "#!/bin/bash" >> "$SCRIPT_FOLDER/fastCalo.sh"
echo "#file name: .sh" >> "$SCRIPT_FOLDER/fastCalo.sh"
echo "source /opt/exp_software/neutrino/env.sh"  >> "$SCRIPT_FOLDER/fastCalo.sh"
echo "source /opt/exp_software/neutrino/ROOT/v6.20.00_py3/bin/thisroot.sh"  >> "$SCRIPT_FOLDER/fastCalo.sh"
echo "LD_LIBRARY_PATH="/opt/exp_software/neutrino/PYTHON3_PACKAGES/:/opt/exp_software/neutrino/ROOT/v6.20.00_py3/lib:$LD_LIBRARY_PATH""  >> "$SCRIPT_FOLDER/fastCalo.sh"
echo "PATH="/opt/exp_software/neutrino/PYTHON3_PACKAGES/:/opt/exp_software/neutrino/ROOT/v6.20.00_py3/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:$PATH"" >> "$SCRIPT_FOLDER/fastCalo.sh"
echo "MANPATH="/opt/exp_software/neutrino/ROOT/v6.20.00_py3/man:$MANPATH:"" >> "$SCRIPT_FOLDER/fastCalo.sh"
echo "python3 $SCRIPT_PATH/fastCalo.py $CONFIG $INPUT $OUTPUT_FOLDER/response_cut.drdf > $LOGS_FOLDER/fastCalo.out.live 2> $LOGS_FOLDER/fastCalo.err.live" >> "$SCRIPT_FOLDER/fastCalo.sh"

# Create the job .sub file
touch "$SCRIPT_FOLDER/fastCalo.sub"
> "$SCRIPT_FOLDER/fastCalo.sub"
echo "environment             = \"PYTHONPATH=/opt/exp_software/neutrino/PYTHON3_PACKAGES\"" >> "$SCRIPT_FOLDER/fastCalo.sub"
# echo "transfer_input_files    =  " >> "$SCRIPT_FOLDER/.sub"
echo "request_cpus = 4" >> "$SCRIPT_FOLDER/fastCalo.sub"
echo "request_memory = 8192" >> "$SCRIPT_FOLDER/fastCalo.sub"
echo "executable              = "$SCRIPT_FOLDER/fastCalo.sh"" >> "$SCRIPT_FOLDER/fastCalo.sub"
#echo "transfer_input_files    = "$EXECUTABLE"" >> "$SCRIPT_FOLDER/fastCalo.sub"
echo "log                     = "$LOGS_FOLDER/fastCalo.log"" >> "$SCRIPT_FOLDER/fastCalo.sub"
#echo "output                  = "$SCRIPT_FOLDER/response_cut.drdf"" >> "$SCRIPT_FOLDER/fastCalo.sub"
echo "error                   = "$LOGS_FOLDER/fastCalo.err"" >> "$SCRIPT_FOLDER/fastCalo.sub"
# echo "should_transfer_files   = Yes" >> "$SCRIPT_FOLDER/.sub"
# echo "when_to_transfer_output = ON_EXIT" >> "$SCRIPT_FOLDER/.sub"
echo "queue" >> "$SCRIPT_FOLDER/fastCalo.sub"


> $LOGS_FOLDER/fastCalo.out
> $LOGS_FOLDER/fastCalo.err
> $LOGS_FOLDER/time.log
check_errors

for ((j=0;j<${REP_NUM};j++)); do
  if [ -f $OUTPUT_FOLDER/response_cut.drdf ]; then 
    rm $OUTPUT_FOLDER/response_cut.drdf
  fi 
  JOB_NUM=${j}
  echo "Submitting job ${JOB_NUM} on HTC"
  condor_submit -name sn-02.cr.cnaf.infn.it -spool "$SCRIPT_FOLDER/fastCalo.sub" > $LOGS_FOLDER/tmp_log
  check_errors
  JOB_ID=$(awk -F "cluster " '{if($2 != "")print $2;if($2 != "") exit;}' "$LOGS_FOLDER/tmp_log")
  JOB_ID=$(echo $JOB_ID | sed "s/\.//g")
  #echo "$JOB_ID" > "$LOGS_FOLDER/tmp_log"
  #JOB_ID=$(head -n 1 $LOGS_FOLDER/tmp_log)
  echo $JOB_ID
  check_condor $JOB_ID 1
  echo "Job ${JOB_NUM} completed"
  JOB_TIME=$(tail -n 1 $LOGS_FOLDER/fastCalo.out.live)
  #JOBNUMBER=$(head -n 2 $LOGS_FOLDER/tmp_log | tail -1)
  echo "Time for job ${JOB_NUM} : ${JOB_TIME}" >> $LOGS_FOLDER/time.log
  #cut -d "---" <<< $LOGS_FOLDER/fastCalo.out.live > $OUTPUT_FOLDER/exe_time.txt
  #grep -n 'number_of_ph=' $LOGS_FOLDER/fastCalo.out.live > $OUTPUT_FOLDER/exe_time.txt
  
done