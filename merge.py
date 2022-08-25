import drdf
import uuid
import sys
import numpy as np

drdf_path = sys.argv[1]
evn_num = sys.argv[2]

# create new drdf
mergefile = drdf.DRDF()
mergefile.start_run(uuid.uuid1())
mergefile.set_georef("DUMMY")

# ---- sort files in numerical order and merge them ---- 
for index in range(int(evn_num)):
    path=drdf_path+'/response_'+str(index)+'.drdf'
    testfile = drdf.DRDF()
    testfile.read(path)
    for run, rundata in testfile.runs.items():
      for event, eventdata in rundata.items():
        mergefile.start_event(event)
        for src, image in eventdata.items():
          mergefile.add_image(src, image)           #add images to new drdf
          
mergefile.write(drdf_path+'/response.drdf')  
