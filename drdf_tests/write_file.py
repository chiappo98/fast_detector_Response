import drdf
import uuid
import numpy as np

testfile = drdf.DRDF()

testfile.start_run(uuid.uuid1())
testfile.set_georef("DUMMY")

testfile.start_event(np.random.randint(0, 65536))

img0 = drdf.Image(np.random.randint(0, 65536, size=(24,24,2), dtype=np.uint16))
testfile.add_image("CAM_NORTH_X05_Y00",img0)

arr = np.random.randint(0, 65536, size=(24,24,2), dtype=np.uint16)
img1 = drdf.Image(24, 24, drdf.Fmtcode.Au16Tu16, arr.tobytes())
testfile.add_image("CAM_NORTH_X05_Y01",img1)

img2 = drdf.Image(24, 24, drdf.Fmtcode.Au16Tu16)
img2.pixels = np.random.randint(0, 65536, size=(24,24,2), dtype=np.uint16)
testfile.add_image("CAM_NORTH_X05_Y02",img2)

testfile.start_event(np.random.randint(0, 65536))

testfile.write('foo.img')
