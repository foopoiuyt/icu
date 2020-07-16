# Copyright (c) 2020, Sony Interactive Entertainment, Inc.
# Copyright (c) 2018, NikitaFeodonit. All rights reserved.
#
## ICU build file for CMake build tools

set(GENRB_TARGETS genrb)
if (NOT MSVC)
  list(APPEND GENRB_TARGETS derb)
endif()
foreach(exe_NAME ${GENRB_TARGETS})
  if(exe_NAME STREQUAL "derb" AND NOT ICU_ENABLE_ICUIO)
    continue()
  endif()

  add_executable(${exe_NAME} "")

  ### Common executables options
  include(${PROJECT_SOURCE_DIR}/common_tools_exe_flags.cmake)

  ### Executable's specifics

  # PRIVATE flags
  set_property(TARGET ${exe_NAME} APPEND PROPERTY
    COMPILE_DEFINITIONS
      UNISTR_FROM_CHAR_EXPLICIT=explicit
      UNISTR_FROM_STRING_EXPLICIT=explicit
  )

  ### Include directories
  # PRIVATE
  target_include_directories(${exe_NAME} PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
    ${PROJECT_SOURCE_DIR}/common
    ${PROJECT_SOURCE_DIR}/i18n
    ${PROJECT_SOURCE_DIR}/tools/toolutil
    ${PROJECT_SOURCE_DIR}/io
  )

  ### Link libraries
  # PRIVATE
  if(exe_NAME STREQUAL "derb")
    # $(LIBICUIO) $(LIBS)
    target_link_libraries(${exe_NAME} PRIVATE ${ICULIBS_IO})
  endif()

  # Common libs must be after the ${ICULIBS_IO}
  include(${PROJECT_SOURCE_DIR}/common_tools_exe_libs.cmake)

  if(exe_NAME STREQUAL "derb")
    target_sources(derb PRIVATE ${CMAKE_CURRENT_LIST_DIR}/derb.cpp)
  else()
    setup_icu_target("${exe_NAME}" "${CMAKE_CURRENT_LIST_DIR}/sources.lst" "${CMAKE_CURRENT_LIST_DIR}")
  endif()

  install(
    TARGETS ${exe_NAME}
    EXPORT "${TARGETS_EXPORT_NAME}"
    ARCHIVE  DESTINATION "${libdir}"
    LIBRARY  DESTINATION "${libdir}"
    RUNTIME  DESTINATION "${bindir}"
    INCLUDES DESTINATION "${includedir}"
  )
endforeach()
