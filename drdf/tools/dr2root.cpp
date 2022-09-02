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

#include <string>
#include <iostream>
#include <drdf.h>
#include <TFile.h>
#include <TTree.h>
#include <TH2F.h>

using namespace drdf;

int main(int argc, char** argv)
 {
  if (argc < 3 || argv[1] == std::string("-h"))
   {
    std::cout << "Usage: " << argv[0] << " <drdf input file> <root output path>" << std::endl;
    std::cout << "[optionally include %r and/or %e in the output file name to obtain a series" << std::endl;
    std::cout << " of files: %r will be replaced by the run UUID, %e by the run number.]" << std::endl;
    return 1;
   }
  auto infile = drdf::drdf::read(argv[1]);
  
  std::string outName; 
              outName += argv[2];
              outName += "/response_tree.root";
  auto outfile = new TFile(outName.c_str(), "RECREATE");
  for (auto run: infile) {
    auto commit_hash = run.second.georef;
    TNamed n(commit_hash.c_str(), "commit hash of the geometry used to generate the file");
    n.Write("commit_hash");
    
    auto runname = to_string(run.first);
    std::cout << "runname: " << runname << std::endl;
    if (!run.second.size())
      continue;
    TTree tree(runname.c_str(), ("Run #" + runname).c_str());
    //FIXME Assumption: all runs start with an event that has all images.
    //If this is not true, we have to scan the whole run and merge all sensor names.
    auto event0 = run.second.begin()->second;
    std::map<std::string, TH2*> hamps;
    std::map<std::string, TH2*> htimes;
    drdf::eventid_t eventid = 0;
    tree.Branch("eventid", &eventid);
    for (auto event : run.second)
     {
      eventid = event.first;
      std::cout << "Looking at event: " << eventid << std::endl;
      for (auto img : event.second)
       {
        auto image = static_cast<const image_t<pixtype_Af32Tf32_t>&>(img.second);
        int sx = image.width();
        int sy = image.height();
        auto name = img.first + "_a";
        auto title = "Amplitude for sensor " + img.first;
        auto haa = new TH2F(name.c_str(), title.c_str(), sx, 0., sx, sy, 0., sy);
        tree.Branch(name.c_str(), haa);
        hamps[img.first] = haa;
        name = img.first + "_t";
        title = "Arrival Time for sensor " + img.first;
        auto htt = new TH2F(name.c_str(), title.c_str(), sx, 0., sx, sy, 0., sy);
        tree.Branch(name.c_str(), htt);
        htimes[img.first] = htt;
    
       
       
       
        auto& ha = hamps[img.first];
        auto& ht = htimes[img.first];
        //FIXME replace with TH2->Set(...);
        for (int x = 0; x < image.width(); ++x)
          for (int y = 0; y < image.height(); ++y)
           {
            int invy = image.height() - y - 1; //DRDF is stored in image coordinates, y is inverted
            std::cout << image.at(x, invy).amplitude << std::endl;
            ha->SetBinContent(x + 1, y + 1, image.at(x, invy).amplitude);
            ht->SetBinContent(x + 1, y + 1, image.at(x, invy).time);
           }
       }
      tree.Fill();
     }
    std::cout << "Writing" << std::endl;
    tree.Write("",TObject::kOverwrite);
   }
  outfile->Close();
  delete outfile;




  outName = ""; 
  outName += argv[2];
  outName += "/response_dir.root";
  outfile = new TFile(outName.c_str() , "RECREATE");
   
  std::map<int, TDirectory*> dirs;
  std::vector<int> eventIDs;

  for (auto run: infile) {
    auto commit_hash = run.second.georef;
    TNamed n(commit_hash.c_str(), "commit hash of the geometry used to generate the file");
    n.Write("commit_hash");
    
    auto runname = to_string(run.first);
    if (!run.second.size())
      continue;
    auto event0 = run.second.begin()->second;
    std::map<std::string, TH2*> hamps;
    std::map<std::string, TH2*> htimes;
    drdf::eventid_t eventid = 0;
    for (auto event : run.second)
     {
      eventid = event.first;
      std::ostringstream ss;
      ss << "event_" << eventid;
      std::string dirname = ss.str();
      TDirectory *dir = outfile->mkdir(dirname.c_str());
      std::cout << dirname << std::endl;
      dir->cd();
      for (auto img : event.second)
       {
       
        auto image = static_cast<const image_t<pixtype_Af32Tf32_t>&>(img.second);
        int sx = image.width();
        int sy = image.height();
        auto name = img.first + "_a";
        auto title = "Amplitude for sensor " + img.first;
        auto haa = new TH2F(name.c_str(), title.c_str(), sx, 0., sx, sy, 0., sy);
        hamps[img.first] = haa;
        name = img.first + "_t";
        title = "Arrival Time for sensor " + img.first;
        auto htt = new TH2F(name.c_str(), title.c_str(), sx, 0., sx, sy, 0., sy);
        htimes[img.first] = htt;
    
       
       
       
        auto& ha = hamps[img.first];
        auto& ht = htimes[img.first];
        //FIXME replace with TH2->Set(...);
        for (int x = 0; x < image.width(); ++x)
          for (int y = 0; y < image.height(); ++y)
           {
            int invy = image.height() - y - 1; //DRDF is stored in image coordinates, y is inverted
            ha->SetBinContent(x + 1, y + 1, image.at(x, invy).amplitude);
            ht->SetBinContent(x + 1, y + 1, image.at(x, invy).time);
           }
          ha->Write();
          ht->Write();
       }
     }
   }
  outfile->Close();
  delete outfile;
 }
