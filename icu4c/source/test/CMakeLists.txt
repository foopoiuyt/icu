# Copyright (c) 2020, Sony Interactive Entertainment, Inc.
#
## ICU build file for CMake build tools

include(CTest)

set(SUBDIRS)

if (ICU_ENABLE_TOOLS)
    list(APPEND SUBDIRS testdata)
endif()

list(APPEND SUBDIRS intltest)

if (ICU_ENABLE_IO)
    list(APPEND SUBDIRS iotest)
endif()

list(APPEND SUBDIRS cintltst)

if (ICU_ENABLE_LAYOUTEX)
    list(APPEND SUBDIRS letest)
endif()

if (ICU_ENABLE_FUZZER)
    list(APPEND SUBDIRS fuzzer)
endif()

# testing
set(SUBDIRS testdata)

foreach(DIR ${SUBDIRS})
    add_subdirectory(${DIR})
endforeach()
