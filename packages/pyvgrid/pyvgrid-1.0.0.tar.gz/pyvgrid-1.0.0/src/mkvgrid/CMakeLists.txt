set(MAIN_SRC main.F90
             posname_nodep.F90)

add_executable(${MKVGRID} ${MAIN_SRC})
target_link_libraries(${MKVGRID} ${STDATM_A})  # link with static stdatm
