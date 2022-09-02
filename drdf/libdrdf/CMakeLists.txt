cmake_minimum_required(VERSION 3.5)
project(DRDF VERSION 0.1 LANGUAGES CXX)
set(CMAKE_CXX_COMPILER /opt/exp_software/neutrino/GCC/gcc-10.2.0/install/bin/g++)

add_library(drdf SHARED
    drdf.cpp
)

target_link_libraries(drdf uuid)

target_include_directories(drdf PUBLIC 
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>  
  $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}/drdf/>)

include(GNUInstallDirs)

install(
    TARGETS
      drdf
    EXPORT
      drdf
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(FILES drdf.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/drdf/)

set(INSTALL_CONFIGDIR ${CMAKE_INSTALL_LIBDIR}/cmake/drdf/)

install(EXPORT drdf DESTINATION ${INSTALL_CONFIGDIR})

