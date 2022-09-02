cmake_minimum_required(VERSION 3.8)
project(DRDFRootConverter VERSION 0.1 LANGUAGES CXX)
set(CMAKE_CXX_COMPILER /opt/exp_software/neutrino/GCC/gcc-10.2.0/install/bin/g++)

include(GNUInstallDirs)

find_package(ROOT)

include_directories(/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-BIN/DRDF-LIB/libdrdf)
link_directories(/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-BIN/DRDF-LIB/libdrdf)

add_executable(dr2root dr2root.cpp)

target_link_libraries(dr2root drdf ROOT::RIO ROOT::Hist ROOT::Core ROOT::Tree)
target_link_options(dr2root PUBLIC "LINKER:-rpath,/usr/local/lib64")

