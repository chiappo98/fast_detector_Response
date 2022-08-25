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

source load_config.sh -c $CONFIG

function setup_prod_dir() {
  mkdir -p $SCRIPT_FOLDER
  mkdir -p $LOGS_FOLDER
  mkdir -p $OUTPUT_FOLDER
  mkdir -p $LOGS_FOLDER/log
  mkdir -p $LOGS_FOLDER/err
  mkdir -p $SCRIPT_FOLDER/many_configs
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

echo "Running splitted_fast_resp over ${EVENT_NUMBER} events, splitted in ${JOBNUMBER} jobs of size ${JOB_SIZE}"
echo "Starting event: ${STARTING_EVENT}"
echo "Input file : ${INPUTFILE}"
echo "Setting up production directory at ${SCRIPT_FOLDER}"
setup_prod_dir
check_errors

touch $SCRIPT_FOLDER/config.txt
> $SCRIPT_FOLDER/config.txt
echo "${RESPONSE_CONFIG}" >> "$SCRIPT_FOLDER/config.txt"                        #configfile
echo "${INPUTFILE}" >> "$SCRIPT_FOLDER/config.txt"                          #path to sensors.root  ---------------->>>>could take as input also the sensor_${ID}.root
echo "${OUTPUT_FOLDER}/response.drdf" >> "$SCRIPT_FOLDER/config.txt"    #output file name
echo "False" >> "$SCRIPT_FOLDER/config.txt"                            #no-cut option
echo "1" >> "$SCRIPT_FOLDER/config.txt"                        #jobNumber
echo "${JOB_SIZE}" >> "$SCRIPT_FOLDER/config.txt"                        #jobSize
echo "${STARTING_EVENT}" >> "$SCRIPT_FOLDER/config.txt"                     #start from event n
echo "False" >> "$SCRIPT_FOLDER/config.txt"                            #idrun
echo "" >> "$SCRIPT_FOLDER/config.txt"

ID=0
while [ $ID -lt $JOBNUMBER ]
do
  cp ${SCRIPT_FOLDER}/config.txt ${SCRIPT_FOLDER}/many_configs/config_${ID}.txt
  SENSOR_NUM=inter_${ID}/sensors_${ID}.root
  RESPONSE_NUM=response_${ID}.drdf
  #if we want to use directly the intermediate root files ----->>>> look if you have to modify also something more!!!!!!!!!!!
  #sed -i "s|sensors.root|${SENSOR_NUM}|g" ${SCRIPT_FOLDER}/many_configs/config_${ID}.txt
  sed -i "s|response.drdf|${RESPONSE_NUM}|g" ${SCRIPT_FOLDER}/many_configs/config_${ID}.txt    #change drdf file name
  sed -i -e '5d' -e "6i${ID}" ${SCRIPT_FOLDER}/many_configs/config_${ID}.txt                    #change job number
  ((ID++))
done

#fast response
echo "Starting splitted_fast_resp response" #>> "$LOGS_FOLDER/calorimetry_response.log"
touch $SCRIPT_FOLDER/splitted_fast_resp.sh
> $SCRIPT_FOLDER/splitted_fast_resp.sh
echo "#!/bin/bash" >> "$SCRIPT_FOLDER/splitted_fast_resp.sh"
echo "#file name: splitted_fast_resp.sh" >> "$SCRIPT_FOLDER/splitted_fast_resp.sh"
echo "source /opt/exp_software/neutrino/env.sh"  >> "$SCRIPT_FOLDER/splitted_fast_resp.sh"
echo "source /opt/exp_software/neutrino/ROOT/v6.20.00_py3/bin/thisroot.sh"  >> "$SCRIPT_FOLDER/splitted_fast_resp.sh"
echo "LD_LIBRARY_PATH="/opt/exp_software/neutrino/PYTHON3_PACKAGES/:/opt/exp_software/neutrino/ROOT/v6.20.00_py3/lib:$LD_LIBRARY_PATH""  >> "$SCRIPT_FOLDER/splitted_fast_resp.sh"
echo "PATH="/opt/exp_software/neutrino/PYTHON3_PACKAGES/:/opt/exp_software/neutrino/ROOT/v6.20.00_py3/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:$PATH"" >> "$SCRIPT_FOLDER/splitted_fast_resp.sh"
echo "MANPATH="/opt/exp_software/neutrino/ROOT/v6.20.00_py3/man:$MANPATH:"" >> "$SCRIPT_FOLDER/splitted_fast_resp.sh"
echo "python3 ${SCRIPT_PATH}/splitted_fast_resp.py \${1}> $LOGS_FOLDER/splitted_fast_resp.out 2> $LOGS_FOLDER/splitted_fast_resp.err" >> "$SCRIPT_FOLDER/splitted_fast_resp.sh"

# Create the job .sub file
touch "$SCRIPT_FOLDER/splitted_fast_resp.sub"
> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
echo "environment             = \"PYTHONPATH=/opt/exp_software/neutrino/PYTHON3_PACKAGES\"" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
echo "request_memory = 8192" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
echo "executable              = "$SCRIPT_FOLDER/splitted_fast_resp.sh"" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
echo "arguments               = "${SCRIPT_FOLDER}/many_configs/config_\$\(Process\).txt"" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
#echo "transfer_input_files    = "$SCRIPT_PATH/splitted_fast_resp2.py"" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
echo "log                     = "$LOGS_FOLDER/log/job_\$\(Process\).log"" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
#echo "output                  = "$OUTPUT_FOLDER/response_\$\(Process\).drdf"" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
echo "error                   = "$LOGS_FOLDER/err/job_\$\(Process\).err"" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
#echo "should_transfer_files   = Yes" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
#echo "when_to_transfer_output = ON_EXIT" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"
echo "queue ${JOBNUMBER}" >> "$SCRIPT_FOLDER/splitted_fast_resp.sub"

start=`date +%s`
echo "Submitting job on HTC"
condor_submit -name sn-02.cr.cnaf.infn.it -spool "${SCRIPT_FOLDER}/splitted_fast_resp.sub" > $LOGS_FOLDER/tmp_log
check_errors
JOB_ID=$(awk -F "cluster " '{if($2 != "")print $2;if($2 != "") exit;}' "$LOGS_FOLDER/tmp_log")
JOB_ID=$(echo ${JOB_ID} | sed "s/\.//g")
#echo "$JOB_ID" > "$LOGS_FOLDER/tmp_log"
#JOB_ID=$(head -n 1 $LOGS_FOLDER/tmp_log)
echo ${JOB_ID}
check_condor ${JOB_ID} ${JOBNUMBER}
echo "Job completed"

end=`date +%s`
echo "Execution time for splitted_fast_resp was `expr $end - $start` seconds." >> $LOGS_FOLDER/time.log

#merge response.drdf files
FILENUMBER=$((${EVENT_NUMBER} / ${JOB_SIZE} ))
echo "Merging drdf files"
python3 ${SCRIPT_PATH}/merge.py ${OUTPUT_FOLDER} ${FILENUMBER}
check_errors
echo "Merge completed"

#analyse response.drdf
if [[ $FAST_ANALYSIS = "yes" ]]; then
  echo "Running fast_analysis.py"
  echo "Setting analysis directory at ${SCRIPT_FOLDER}/output_analysis"
  mkdir -p ${SCRIPT_FOLDER}/output_analysis
  python3 ${SCRIPT_PATH}/fast_analysis.py ${OUTPUT_FOLDER}/response.drdf ${EDEPFILE} ${SCRIPT_FOLDER}/output_analysis ${EVENT_NUMBER} ${STARTING_EVENT} ${PLOT_CAMERAS}
  check_errors
  echo "Anlaysis completed"
fi  
