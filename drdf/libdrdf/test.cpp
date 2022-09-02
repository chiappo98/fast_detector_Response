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

#include "drdf.h"
#include <iostream>
#include <random>

using namespace drdf;

int main(int argc, char** argv)
 {
  if (argc < 3)
    return - 1;
  std::default_random_engine generator(0xdeadbeef);
  std::uniform_int_distribution<unsigned short> distribution(0,65535);
  std::string cmd(argv[1]);
  std::string fname(argv[2]);
  if (cmd == "create")
   {
    drdf::drdf imagefiles;
    auto uuid = get_uuid();
    imagefiles.start_run(uuid);
    std::cout << "Created new run: " << to_string(uuid) << std::endl;
    eventid_t evn = distribution(generator);
    imagefiles.start_event(evn);
    std::cout << "Created new event: " << evn << std::endl;
    sourceid_t src = "CAM_NORTH_X05_Y00";
    image_t<pixtype_Au16_t> img(24, 24);
    for (int i = 0; i != 24*24; ++i)
      img.pixels()[i].amplitude = distribution(generator);
    imagefiles.add_image(src, img);
    std::cout << "Written image for source: " << src << std::endl;
    for (int i = 0; i != 24*24; ++i)
      img.pixels()[i].amplitude = distribution(generator);
    src = "CAM_NORTH_X05_Y01";
    imagefiles.add_image(src, img);
    std::cout << "Written image for source: " << src << std::endl;
    for (int i = 0; i != 24*24; ++i)
      img.pixels()[i].amplitude = distribution(generator);
    src = "CAM_NORTH_X05_Y02";
    imagefiles.add_image(src, img);
    std::cout << "Written image for source: " << src << std::endl;
    evn = distribution(generator);
    imagefiles.start_event(evn);
    std::cout << "Created new event: " << evn << std::endl;
    imagefiles.write(fname);
   }
  if (cmd == "read")
   {
    auto file = drdf::drdf::read(fname);
    for (auto run: file)
     {
      std::cout << "Found run \"" << to_string(run.first) << "\" with " << run.second.size() << " events.\n";
      for (auto event : run.second)
       {
        std::cout << "Found event \"" << event.first << "\" with " << event.second.size() << " images.\n";
        for (auto img : event.second)
          std::cout << "Found image for source \"" << img.first << "\" with size " << img.second.size() << std::endl;
       }
     }
   }
 }
