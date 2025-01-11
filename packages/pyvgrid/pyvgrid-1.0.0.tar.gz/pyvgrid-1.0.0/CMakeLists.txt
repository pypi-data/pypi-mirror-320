cmake_minimum_required(VERSION 3.1)

project(vgrid
        DESCRIPTION "Vertical hybrid-pressure grids"
        LANGUAGES Fortran)
enable_language(Fortran)

set(CMAKE_Fortran_FLAGS ${CMAKE_Fortran_FLAGS} "-g -fPIC")

# targets names
set(MKVGRID mkvgrid.x)
set(STDATM_SO stdatm)
set(STDATM_A _stdatm)

# Source code
add_subdirectory(src/stdatm)
add_subdirectory(src/mkvgrid)

install(TARGETS ${MKVGRID} DESTINATION ${CMAKE_INSTALL_BINDIR})
install(TARGETS ${STDATM_SO} LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
