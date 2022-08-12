import drdf
import uuid
import numpy as np

testfile = drdf.DRDF()
testfile.read('foo.img')
for run, rundata in testfile.runs.items():
  print('Run', run, 'with', len(rundata), 'events')
  print(' with geometry', rundata.georef)
  for event, eventdata in rundata.items():
    print('Event', event, 'with', len(eventdata), 'images')
    for src, image in eventdata.items():
      print('Image from source', src, 'with size', image.pixels.shape)
