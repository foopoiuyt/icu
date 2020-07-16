# Copyright (c) 2020, Sony Interactive Entertainment, Inc.

function(load_icu_sources VARIABLE SOURCE_FILE BASE_DIR)
  file(STRINGS ${SOURCE_FILE} LOAD_SOURCES_FILES)
#  message(WARNING "${LOAD_SOURCES_FILES}")
  foreach(LOAD_SOURCES_FILE ${LOAD_SOURCES_FILES})
    list(APPEND ${VARIABLE} "${BASE_DIR}/${LOAD_SOURCES_FILE}")
  endforeach()
  set(${VARIABLE} ${${VARIABLE}} PARENT_SCOPE)
endfunction()

macro(get_icu_private_headers VARIABLE DIR)
  file(GLOB ${VARIABLE} "${DIR}/*.h")
endmacro()

macro(get_icu_public_headers_old VARIABLE DIR)
  file(GLOB ${VARIABLE} "${DIR}/unicode/*.h")
endmacro()

function(get_icu_public_headers VARIABLE SEARCH_DIR OUT_DIR)
  file(GLOB ${VARIABLE}_HEADERS "${SEARCH_DIR}/unicode/*.h")
  foreach(HEADER ${${VARIABLE}_HEADERS})
    file(RELATIVE_PATH HEADER_REL ${SEARCH_DIR} ${HEADER})
    list(APPEND ${VARIABLE} "${OUT_DIR}/${HEADER_REL}")
  endforeach()
  set(${VARIABLE} ${${VARIABLE}} PARENT_SCOPE)
endfunction()

macro(setup_icu_target TARGET SOURCE_FILE SOURCE_DIR)
  load_icu_sources(${TARGET}_SOURCES ${SOURCE_FILE} ${SOURCE_DIR})
  get_icu_private_headers(${TARGET}_PRIVATE_HEADERS ${SOURCE_DIR})
  get_icu_public_headers_old(${TARGET}_PUBLIC_HEADERS ${SOURCE_DIR})

  target_sources(${TARGET} PRIVATE ${${TARGET}_SOURCES} ${${TARGET}_PRIVATE_HEADERS} PUBLIC ${${TARGET}_PUBLIC_HEADERS})
endmacro()

function(setup_icu_lib_target TARGET SOURCES_FILE SOURCE_DIR PUBLIC_DIR)
  load_icu_sources(${TARGET}_SOURCES ${SOURCES_FILE} ${SOURCE_DIR})
  get_icu_private_headers(${TARGET}_PRIVATE_HEADERS ${SOURCE_DIR})
  get_icu_public_headers(${TARGET}_PUBLIC_HEADERS ${SOURCE_DIR} ${PUBLIC_DIR})

  target_sources(${TARGET} PRIVATE ${${TARGET}_SOURCES} ${${TARGET}_PRIVATE_HEADERS} PUBLIC ${${TARGET}_PUBLIC_HEADERS})

  set(${TARGET}_SOURCES ${${TARGET}_SOURCES} PARENT_SCOPE)
  set(${TARGET}_PRIVATE_HEADERS ${${TARGET}_PRIVATE_HEADERS} PARENT_SCOPE)
  set(${TARGET}_PUBLIC_HEADERS ${${TARGET}_PUBLIC_HEADERS} PARENT_SCOPE)
endfunction()

function(setup_icu_exe_target TARGET SOURCES_FILE SOURCE_DIR)
  load_icu_sources(${TARGET}_SOURCES ${SOURCES_FILE} ${SOURCE_DIR})
  get_icu_private_headers(${TARGET}_PRIVATE_HEADERS ${SOURCE_DIR})

  target_sources(${TARGET} PRIVATE ${${TARGET}_SOURCES} ${${TARGET}_PRIVATE_HEADERS})
  set(${VARIABLE}_SOURCES ${${VARIABLE}} PARENT_SCOPE)
  set(${VARIABLE}_PRIVATE_HEADERS ${${VARIABLE}_PRIVATE_HEADERS} PARENT_SCOPE)
endfunction()

function(add_prefix VARIABLE PREFIX)
  set(${VARIABLE})
  foreach(ELEMENT ${ARGN})
    list(APPEND ${VARIABLE} "${PREFIX}/${ELEMENT}")
  endforeach()
  set(${VARIABLE} ${${VARIABLE}} PARENT_SCOPE)
endfunction()

function(make_custom_command_and_target TARGET OUTPUT)
  add_custom_command(OUTPUT ${OUTPUT} ${ARGN})
  add_custom_target(${TARGET} DEPENDS ${DEP})
endfunction()
