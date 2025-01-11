set(SRC altsta.F90
        presta.F90)

add_library(${STDATM_A} STATIC ${SRC})
add_library(${STDATM_SO} SHARED ${SRC})
