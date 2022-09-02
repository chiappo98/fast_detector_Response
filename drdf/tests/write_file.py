#
# Copyright 2020-2022 N. Tosi, V. Pia <nicolo.tosi@bo.infn.it>
#
# This program is free software:
# you can redistribute it and/or modify it under the terms of the GNU
# Lesser General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

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
