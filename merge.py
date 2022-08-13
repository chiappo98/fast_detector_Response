import drdf
import uuid
import sys
import numpy as np

#/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-GRAIN-CALORIMETRY/scratch/fastCalo_submission/parallel_200_400reduced/output/
#drdf_path = '/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-GRAIN-CALORIMETRY/scratch/fastCalo_submission/parallel_500_510edep/output'
drdf_path = sys.argv[1]
evn_num = sys.srgv[2]

mergefile = drdf.DRDF()
mergefile.start_run(uuid.uuid1())
mergefile.set_georef("DUMMY")

#paths = Path(drdf_path).glob('**/*.drdf')        #doesn't sort numerically the files
#for path in paths:  
for index in range(int(evn_num)):
    path=drdf_path+'/response_'+str(index)+'.drdf'
    testfile = drdf.DRDF()
    testfile.read(path)
    for run, rundata in testfile.runs.items():
      #print('Run', run, 'with', len(rundata), 'events')
      #print(' with geometry', rundata.georef)
      for event, eventdata in rundata.items():
        mergefile.start_event(event)
        #print('Event', event, 'with', len(eventdata), 'images')
        for src, image in eventdata.items():
          #print('Image from source', src, 'with size', image.pixels.shape)
          mergefile.add_image(src, image)
          
mergefile.write(drdf_path+'/response.drdf')  
