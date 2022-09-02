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

from binascii import crc32
import collections
import numpy
import struct
import uuid
from enum import IntEnum

class Fmtcode(IntEnum):
    Au8 = 0
    Au8Tu8 = 1
    Au16 = 2
    Au16Tu16 = 3
    Af32Tf32 = 4

def _decode_fmt(x, y, fmt):
  if fmt == Fmtcode.Au8 or fmt == Fmtcode.Au8Tu8:
    dtype = numpy.uint8
  elif fmt == Fmtcode.Au16 or fmt == Fmtcode.Au16Tu16:
    dtype = numpy.uint16
  elif fmt == Fmtcode.Af32Tf32:
    dtype = numpy.float32
  else:
    raise TypeError('Invalid Format: {0}'.format(fmt))
  if fmt == Fmtcode.Au8 or fmt == Fmtcode.Au16:
    shape = (x, y)
  else:
    shape = (x, y, 2)
  return shape, dtype

def _encode_fmt(shape, dtype):
  if len(shape) == 2:
    if dtype == numpy.uint8:
      fmtcode = Fmtcode.Au8
    elif dtype == numpy.uint16:
      fmtcode = Fmtcode.Au16
    else:
      raise TypeError('Invalid dtype: {0}'.format(dtype))
  elif len(shape) == 3 and shape[2] == 2:
    if dtype == numpy.uint8:
      fmtcode = Fmtcode.Au8Tu8
    elif dtype == numpy.uint16:
      fmtcode = Fmtcode.Au16Tu16
    elif dtype == numpy.float32:
      fmtcode = Fmtcode.Af32Tf32
    else:
      raise TypeError('Invalid dtype: {0}'.format(dtype))
  else:
      raise TypeError('Invalid shape: {0}'.format(shape))
  return shape[0], shape[1], fmtcode

class Image:

  def __init__(self, w, h=None, fmt=None, rawbytes=None):
    try:
      self.width, self.height, self.fmtcode = _encode_fmt(w.shape, w.dtype)
      self.pixels = w
    except:
      self.width = w
      self.height = h
      self.fmtcode = fmt
      shape, dtype = _decode_fmt(w, h, fmt)
      if rawbytes is None:
        self.pixels = numpy.zeros(shape=shape, dtype=dtype, order='C')
      else:
        self.pixels = numpy.frombuffer(rawbytes, dtype=dtype)
        self.pixels = numpy.reshape(self.pixels, shape, order='C')

  def bytes(self):
    return self.pixels.tobytes()

def _write_chunk(f, tag, buf, crc):
  head = struct.pack('<I4s', len(buf), tag)
  crc = crc32(head, crc)
  f.write(head)
  crc = crc32(buf, crc)
  f.write(buf)
  return crc

_expected_chunk_lengths = {
  b'HRAW': 0,
  b'RSTA':16,
  b'EVNT': 4,
  b'IFMT': 8,
  b'ERAW': 4
 }

def _read_chunk(f, crc):
  head = f.read(8)
  length, tag = struct.unpack('<I4s', head)
  if tag in _expected_chunk_lengths and _expected_chunk_lengths[tag] != length:
    raise IOError('Chunk size does not match expected value')
  crc = crc32(head, crc)
  body = f.read(length)
  if tag != b'ERAW':
    crc = crc32(body, crc)
  return tag, body, crc

class DRDF:

  def __init__(self):
    self.runs = collections.OrderedDict()

  def start_run(self, run_uuid):
    self.current_run = collections.OrderedDict()
    self.runs[run_uuid] = self.current_run
    self.current_event = None

  def set_georef(self, georef):
    self.current_run.georef = georef

  def start_event(self, event_id):
    self.current_event = collections.OrderedDict()
    self.current_run[event_id] = self.current_event

  def add_image(self, source, image):
    self.current_event[source] = image

  def read(self, fname):
    with open(fname, mode='rb') as f:
      crc = 0xFFFFFFFF
      buf = f.read(8)
      if buf != b'\x00\x00\x00\x00HRAW':
        raise IOError('File header does not match')
      crc = crc32(buf, crc)
      current_chunk = b'HRAW'
      while current_chunk != b'ERAW':
        current_chunk, chunk_data, crc = _read_chunk(f, crc)
        if current_chunk == b'ERAW':
          crc_in_file, = struct.unpack('<I', chunk_data)
          if crc_in_file != crc:
            raise IOError('Checksum mismatch: calculated {0:08X}, expected {1:08X}'.format(crc, crc_in_file))
        elif current_chunk == b'RSTA':
          run_uuid = uuid.UUID(bytes=chunk_data)
          self.start_run(run_uuid)
        elif current_chunk == b'RGEO':
          georef = chunk_data.decode('ascii')
          self.set_georef(georef)
        elif current_chunk == b'EVNT':
          evnum = struct.unpack('<I', chunk_data)[0]
          self.start_event(evnum)
        elif current_chunk == b'IFMT':
          current_shape, current_dtype = _decode_fmt(*struct.unpack('<HHBxxx', chunk_data))
        elif current_chunk == b'ISRC':
          current_source = chunk_data.decode('ascii')
        elif current_chunk == b'IDAT':
          pixels = numpy.frombuffer(chunk_data, dtype=current_dtype)
          self.add_image(current_source, Image(numpy.reshape(pixels, current_shape, order='C')))

  def write(self, fname):
    crc = 0xFFFFFFFF
    with open(fname, mode='wb') as f:
      crc = _write_chunk(f, b'HRAW', bytes(), crc);
      for run_uuid, rundata in self.runs.items():
        crc = _write_chunk(f, b'RSTA', run_uuid.bytes, crc)
        crc = _write_chunk(f, b'RGEO', bytes(rundata.georef, 'ascii'), crc)
        for event_id, eventdata in rundata.items():
          crc = _write_chunk(f, b'EVNT', struct.pack('<I', event_id), crc)
          for img_src, img in eventdata.items():
            crc = _write_chunk(f, b'ISRC', bytes(img_src, 'ascii'), crc)
            crc = _write_chunk(f, b'IFMT', struct.pack('<HHBxxx', img.width, img.height, img.fmtcode), crc)
            crc = _write_chunk(f, b'IDAT', img.bytes(), crc)
      end = b'\x04\0\0\0ERAW';
      crc = crc32(end, crc);
      crcbytes = struct.pack('<I', crc)
      _write_chunk(f, b'ERAW', crcbytes, crc);
