#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "tetgenpy::tetgen" for configuration "Release"
set_property(TARGET tetgenpy::tetgen APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(tetgenpy::tetgen PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/tetgen.lib"
  )

list(APPEND _cmake_import_check_targets tetgenpy::tetgen )
list(APPEND _cmake_import_check_files_for_tetgenpy::tetgen "${_IMPORT_PREFIX}/lib/tetgen.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
