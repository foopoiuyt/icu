# Copyright (c) 2020, Sony Interactive Entertainment, Inc.
#
## ICU build file for CMake build tools

# relative lib links from pkgdata are the same as for tmp
set(GENRBOPTS -k)

# use the cross root, in case we are cross compiling. Otherwise it is equal to top_builddir

set(TOOLDIR ${TOOLBINDIR}/tools)

set(SRCDATADIR ${CMAKE_SOURCE_DIR}/data)
set(UNICODEDATADIR ${SRCDATADIR}/unidata)
set(OUTDIR ${CMAKE_BINARY_DIR}/data/out)
set(OUTTMPDIR ${CMAKE_BINARY_DIR}/data/out/tmp)
set(BUILDDIR ${OUTDIR}/build/${ICUDATA_PLATFORM_NAME})
set(TESTSRCDATADIR ${CMAKE_SOURCE_DIR}/test/testdata)
set(TESTOUTDIR ${CMAKE_BINARY_DIR}/test/testdata/out)
# Contains all 'intermediate' files (and temp files) except for 'unpackaged data' below
set(TESTBUILDDIR ${TESTOUTDIR}/build)
set(BUILD_DIRS ${TESTOUTDIR} ${TESTBUILDDIR} ${TESTOUTDIR}/${TESTDT})
set(GENTEST ${TOOLBINDIR}/gentest) # $(TOOLEXEEXT)

if(PKGDATA_MODE STREQUAL "common")
    set(ICU_DATA_OPT -i ${OUTDIR})
elseif(NOT PKGDATA_MODE STREQUAL "dll" OR ENABLE_STATIC)
    set(ICU_DATA_OPT -i ${BUILDDIR})
endif()

set(CURDIR ${CMAKE_CURRENT_LIST_DIR})

set(PKGDATA ${TOOLBINDIR}/pkgdata -q -c -s ${CURDIR}/out/build/${ICUDATA_PLATFORM_NAME})

# unpackaged files  - live in 'out' so that the path can find them as part of the pkg
set(UNPACKAGEDTESTDATA ${TESTOUTDIR}/${TESTDT}/nam.typ)

# pkg name for testdata
set(TESTDATA testdata)
# prefix for files that are testdata
set(TESTDT ${TESTDATA})

# Variable names for rules.mk
set(OUT_DIR ${TESTBUILDDIR})
set(TMP_DIR ${TESTOUTDIR}/${TESTDT})

set(OLDPYTHONPATH $ENV{PYTHONPATH})
set(ENV{PYTHONPATH} "${CMAKE_SOURCE_DIR}/source/python")
execute_process(COMMAND
  python -m icutools.databuilder --mode cmake --seqmode parallel
         --src_dir ${CMAKE_CURRENT_LIST_DIR}
         --out_dir ${OUT_DIR}
         --tmp_dir ${TMP_DIR}
  OUTPUT_FILE ${CMAKE_CURRENT_BINARY_DIR}/rules.cmake
)
set(ENV{PYTHONPATH} ${OLDPYTHONPATH})

include("${CMAKE_CURRENT_BINARY_DIR}/rules.cmake")

add_custom_target(
  packagetest
  COMMAND ${PKGDATA} -T ${TESTBUILDDIR} -d ${TESTOUTDIR} -s ${TESTBUILDDIR} -p ${TESTDATA} -m common ${TMP_DIR}/testdata.lst
  DEPENDS pkgdata ${TMP_DIR}/testdata.lst ${TESTDATA_ALL_OUTPUT_FILES}
)
