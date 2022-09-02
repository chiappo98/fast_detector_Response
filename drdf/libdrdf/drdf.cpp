/*
 * Copyright 2020-2022 N. Tosi, V. Pia <nicolo.tosi@bo.infn.it>
 *
 * This program is free software:
 * you can redistribute it and/or modify it under the terms of the GNU
 * Lesser General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include <algorithm>
#include <cstring>
#include <fstream>
#include <memory>
#include <stdexcept>

#include "drdf.h"

namespace drdf
 {

  enum chunktype_t
   {
    HRAW = 0,
    ERAW = 1,
    RSTA = 2,
    RCCD = 3,
    RGEO = 4,
    EVNT = 5,
    IDAT = 6,
    ISRC = 7,
    IFMT = 8,
    _LAST = 9
   };

  static const char chunknames[_LAST][5] = {
    "HRAW",
    "ERAW",
    "RSTA",
    "RCCD",
    "RGEO",
    "EVNT",
    "IDAT",
    "ISRC",
    "IFMT",
   };

  static const uint32_t pixsizes[] =
   {
    1,
    2,
    2,
    4,
    8
   };

  run_uuid_t get_uuid()
   {
    run_uuid_t rui;
    ::uuid_generate_time(rui.uuid);
    return rui;
   }

  std::string to_string(const run_uuid_t& uuid)
   {
    std::string buf(36, '-');
    ::uuid_unparse_lower(uuid.uuid, const_cast<char*>(buf.data()));
    return buf;
   }

  static_assert(sizeof(ifmt_t)==8);

  uint32_t ifmt_t::size() const
   {
    return size_x * size_y * pixsizes[pixelfmt];
   }

  image_base_t::image_base_t(ifmt_t fmt):
   m_format(fmt)
   {
    m_array_data = ::operator new(m_format.size());
   }

  image_base_t::image_base_t(ifmt_t fmt, const void* src):
   m_format(fmt)
   {
    m_array_data = ::operator new(m_format.size());
    std::memcpy(m_array_data, src, m_format.size());
   }

  image_base_t::~image_base_t()
   {
    ::operator delete(m_array_data);
   }

  image_base_t::image_base_t(image_base_t&& rhs):
   m_format(), m_array_data(nullptr)
   {
    *this = std::move(rhs);
   }

  image_base_t::image_base_t(const image_base_t& rhs):
   m_format(rhs.m_format)
   {
    size_t alloc = m_format.size();
    m_array_data = ::operator new(alloc);
    std::memcpy(m_array_data, rhs.m_array_data, alloc);
   }

  image_base_t& image_base_t::operator = (image_base_t&& rhs)
   {
    std::swap(m_format, rhs.m_format);
    std::swap(m_array_data, rhs.m_array_data);
    return *this;
   }

  drdf::drdf() :
   m_runs(), m_run(m_runs.end())
   {}

  void drdf::start_run(run_uuid_t uuid)
   {
    m_run = m_runs.emplace(uuid, run_map_t()).first;
    m_event = m_run->second.end();
   }

  void drdf::set_georef(const uri_t& ref)
   {
    m_run->second.georef = ref;
   }

  void drdf::start_event(eventid_t evnt)
   {
    if (m_run == m_runs.end())
      throw std::out_of_range("Cannot add events outside of runs");
    m_event = m_run->second.emplace(evnt, event_map_t()).first;
   }

  drdf drdf::read(uri_t fname)
   {
    std::ifstream file(fname.c_str(), std::ios::binary | std::ios::ate);
    if (!file)
      throw std::invalid_argument("Cannot open " + fname);
    std::streamsize size = file.tellg();
    file.seekg(0, std::ios::beg);
    std::unique_ptr<char[]> buffer(new char[size]);
    file.read(buffer.get(), size);
    const char* read = buffer.get();
    const char* end = read + size;
    if (size < 20 || std::memcmp(read, "\0\0\0\0HRAW", 8))
      throw std::invalid_argument(fname + " is not a valid Detector Response file.");
    checksum_t checksum = crc32(0xFFFFFFFFu, read, end - 4);
    checksum_t crc_in_file;
    read += 8;
    run_uuid_t current_run;
    eventid_t current_event;
    sourceid_t current_source;
    ifmt_t current_ifmt;
    chunktype_t current_chunk = HRAW;
    bool got_end = false;
    drdf ret;
    while (current_chunk != ERAW)
     {
      uint32_t chunklen = *reinterpret_cast<const uint32_t*>(read);
      read += 4;
      int ct = 0;
      while (std::memcmp(chunknames[ct], read, 4) && ct < _LAST)
        ++ct;
      current_chunk = chunktype_t(ct);
      if (current_chunk == _LAST)
        throw std::invalid_argument(fname + " contains chunk of invalid type: "
                                    + std::string(read,4));
      read += 4;
      if (end - read < chunklen)
        throw std::out_of_range(fname + " contains chunk of invalid length: "
                                + std::to_string(chunklen) + " (exceeds file size)");
      switch (current_chunk)
       {
        case HRAW:
        break;
        case ERAW:
        crc_in_file = *reinterpret_cast<const checksum_t*>(read);
        if (crc_in_file != checksum)
          throw std::invalid_argument(fname + " checksum does not match, got: "
                                      + std::to_string(checksum)
                                      + ", expected: " + std::to_string(crc_in_file));
        got_end = true;
        break;
        case RSTA:
        if (chunklen != 16)
          throw std::out_of_range(fname + " contains RSTA chunk of invalid length: "
                                  + std::to_string(chunklen) + " (expected 16)");
        current_run = *reinterpret_cast<const run_uuid_t*>(read);
        ret.m_runs.emplace(current_run, run_map_t());
        break;
        case RCCD:
        // do nothing  std::string(read, read + chunklen);
        break;
        case RGEO:
        ret.m_runs[current_run].georef = std::string(read, read + chunklen);
        break;
        case EVNT:
        if (chunklen != 4)
          throw std::out_of_range(fname + " contains EVNT chunk of invalid length: "
                                  + std::to_string(chunklen) + " (expected 4)");
        current_event = *reinterpret_cast<const uint32_t*>(read);
        ret.m_runs[current_run].emplace(current_event, event_map_t());
        break;
        case IFMT:
        if (chunklen != sizeof(ifmt_t))
          throw std::out_of_range(fname + " contains IFMT chunk of invalid length: "
                                  + std::to_string(chunklen) + " (expected 8)");
        current_ifmt = *reinterpret_cast<const ifmt_t*>(read);
        break;
        case ISRC:
        current_source = std::string(read, read + chunklen);
        break;
        case IDAT:
        if (chunklen != current_ifmt.size())
          throw std::out_of_range("IDAT chunk has invalid length: " + std::to_string(chunklen)
                                  + " (expected " + std::to_string(current_ifmt.size()) + ")");
        ret.m_runs[current_run][current_event].emplace(current_source, image_base_t(current_ifmt, read));
        break;
        case _LAST:
        //cannot reach, handled before switch
        break;
       };
      read += chunklen;
     }
    if (!got_end)
      throw std::invalid_argument(fname + " is incomplete (ERAW tag missing)");
    return ret;
   }

  checksum_t drdf::write_chunk(std::ofstream& file, const char* tag, uint32_t len, const void* data, checksum_t crc)
   {
    char buffer[8];
    std::memcpy(buffer, &len, 4);
    std::memcpy(buffer + 4, tag, 4);
    file.write(buffer, 8);
    crc = crc32(crc, buffer, buffer + 8);
    const char* pdata = static_cast<const char*>(data);
    file.write(pdata, len);
    return crc32(crc, pdata, pdata + len);
   }

  void drdf::write(uri_t fname)
   {
    std::ofstream file(fname.c_str(), std::ios::out | std::ios::binary);
    checksum_t crc = 0xFFFFFFFFu;
    crc = write_chunk(file, chunknames[HRAW], 0, nullptr, crc);
    for (const auto& run: m_runs)
     {
      crc = write_chunk(file, chunknames[RSTA], sizeof(run_uuid_t), &run.first, crc);
      auto georef = run.second.georef;
      crc = write_chunk(file, chunknames[RGEO], georef.size(), georef.c_str(), crc);
      for (const auto& event: run.second)
       {
       crc = write_chunk(file, chunknames[EVNT], 4, &event.first, crc);
        for (const auto& image: event.second)
         {
          crc = write_chunk(file, chunknames[ISRC], image.first.size(), image.first.c_str(), crc);
          crc = write_chunk(file, chunknames[IFMT], sizeof(ifmt_t), &image.second.format(), crc);
          crc = write_chunk(file, chunknames[IDAT], image.second.size(), image.second.pixels(), crc);
         }
       }
     }
    const char end[9] = "\x04\0\0\0ERAW";
    crc = crc32(crc, end, end + 8);
    write_chunk(file, chunknames[ERAW], 4, &crc, crc);
   }

  std::array<checksum_t, 256> drdf::generate_crc_table()
   {
    std::array<checksum_t, 256> table;
    checksum_t rem;
    for (int i = 0; i < 256; i++)
     {
      rem = i;  /* remainder from polynomial division */
      for (int j = 0; j < 8; j++)
       {
        if (rem & 1)
         {
          rem >>= 1;
          rem ^= 0xedb88320ul;
         }
        else
          rem >>= 1;
       }
      table[i] = rem;
     }
    return table;
   }

  checksum_t drdf::crc32(checksum_t partial, const char* begin, const char* end)
   {
    static std::array<checksum_t, 256> table = generate_crc_table();
    checksum_t crc = ~partial;
    for ( ; begin < end; ++begin)
     crc = (crc >> 8) ^ table[(crc & 0xff) ^ uint8_t(*begin)];
    return ~crc;
   }

 }
