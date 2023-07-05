cmake_minimum_required(VERSION 3.18)
cmake_policy(VERSION 3.18)

project(T3FF)



set(CMAKE_CXX_STANDARD 17)

set(library "libt3ff")

set(bindings_library "t3ff")
set(bindings_header ${CMAKE_SOURCE_DIR}/bindings.h)
set(typesystem ${CMAKE_SOURCE_DIR}/bindings.xml)

set(generated_sources
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/counter_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/t3ff_module_wrapper.cpp)



if(NOT python_interpreter)
    if(WIN32 AND "${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
        find_program(python_interpreter "python_d")
        if(NOT python_interpreter)
            message(FATAL_ERROR
                "A debug Python interpreter could not be found, which is a requirement when "
                "building this example in a debug configuration. Make sure python_d.exe is in "
                "PATH.")
        endif()
    else()
        find_program(python_interpreter "python")
        if(NOT python_interpreter)
            message(FATAL_ERROR
                "No Python interpreter could be found. Make sure python is in PATH.")
        endif()
    endif()
endif()
message(STATUS "Using python interpreter: ${python_interpreter}")

# Macro to get various pyside / python include / link flags and paths.
# Uses the not entirely supported utils/pyside_config.py file.
macro(pyside_config option output_var)
    if(${ARGC} GREATER 2)
        set(is_list ${ARGV2})
    else()
        set(is_list "")
    endif()

    execute_process(
      COMMAND ${python_interpreter} "/home/louis/Python/blaise/venv/lib/python3.10/site-packages/PySide6/examples/utils/pyside_config.py"
              ${option}
      OUTPUT_VARIABLE ${output_var}
      OUTPUT_STRIP_TRAILING_WHITESPACE)

    if ("${${output_var}}" STREQUAL "")
        message(FATAL_ERROR "Error: Calling pyside_config.py ${option} returned no output.")
    endif()
    if(is_list)
        string (REPLACE " " ";" ${output_var} "${${output_var}}")
    endif()
endmacro()

# Query for the shiboken generator path, Python path, include paths and linker flags.
pyside_config(--shiboken-module-path shiboken_module_path)
pyside_config(--shiboken-generator-path shiboken_generator_path)
pyside_config(--python-include-path python_include_dir)
pyside_config(--shiboken-generator-include-path shiboken_include_dir 1)
pyside_config(--shiboken-module-shared-libraries-cmake shiboken_shared_libraries 0)
pyside_config(--python-link-flags-cmake python_linking_data 0)

set(shiboken_path "${shiboken_generator_path}/shiboken6${CMAKE_EXECUTABLE_SUFFIX}")
if(NOT EXISTS ${shiboken_path})
    message(FATAL_ERROR "Shiboken executable not found at path: ${shiboken_path}")
endif()


# ==================================== RPATH configuration ====================================


# =============================================================================================
# !!! (The section below is deployment related, so in a real world application you will want to
# take care of this properly with some custom script or tool).
# =============================================================================================
# Enable rpaths so that the built shared libraries find their dependencies.
set(CMAKE_SKIP_BUILD_RPATH FALSE)
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
set(CMAKE_INSTALL_RPATH ${shiboken_module_path} "$ORIGIN")
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
# =============================================================================================
# !!! End of dubious section.
# =============================================================================================


# =============================== CMake target - library ===============================


# Define the sample shared library for which we will create bindings.
set(${library}_sources test.cpp)
add_library(${library} SHARED ${${library}_sources})
set_property(TARGET ${library} PROPERTY PREFIX "")

# Needed mostly on Windows to export symbols, and create a .lib file, otherwise the binding
# library can't link to the sample library.
target_compile_definitions(${library} PRIVATE BINDINGS_BUILD)


# ====================== Shiboken target for generating binding C++ files  ====================


# Set up the options to pass to shiboken.
set(shiboken_options --generator-set=shiboken --enable-parent-ctor-heuristic
    --enable-return-value-heuristic --use-isnull-as-nb_nonzero
    --avoid-protected-hack
    -I${CMAKE_SOURCE_DIR}
    -T${CMAKE_SOURCE_DIR}
    --output-directory=${CMAKE_CURRENT_BINARY_DIR}
    )

set(generated_sources_dependencies ${bindings_header} ${typesystem})

# Add custom target to run shiboken to generate the binding cpp files.
add_custom_command(OUTPUT ${generated_sources}
                    COMMAND ${shiboken_path}
                    ${shiboken_options} ${bindings_header} ${typesystem}
                    DEPENDS ${generated_sources_dependencies}
                    IMPLICIT_DEPENDS CXX ${bindings_header}
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                    COMMENT "Running generator for ${typesystem}.")


# =============================== CMake target - bindings_library =============================


# Set the cpp files which will be used for the bindings library.
set(${bindings_library}_sources ${generated_sources})

# Define and build the bindings library.
add_library(${bindings_library} MODULE ${${bindings_library}_sources})

# Apply relevant include and link flags.
target_include_directories(${bindings_library} PRIVATE ${python_include_dir})
target_include_directories(${bindings_library} PRIVATE ${shiboken_include_dir})
target_include_directories(${bindings_library} PRIVATE ${CMAKE_SOURCE_DIR})

target_link_libraries(${bindings_library} PRIVATE ${shiboken_shared_libraries})
target_link_libraries(${bindings_library} PRIVATE ${library})

# Adjust the name of generated module.
set_property(TARGET ${bindings_library} PROPERTY PREFIX "")
set_property(TARGET ${bindings_library} PROPERTY OUTPUT_NAME
             "${bindings_library}${PYTHON_EXTENSION_SUFFIX}")
if(WIN32)
    if("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
        set_property(TARGET ${bindings_library} PROPERTY SUFFIX "_d.pyd")
    else()
        set_property(TARGET ${bindings_library} PROPERTY SUFFIX ".pyd")
    endif()
endif()

# Make sure the linker doesn't complain about not finding Python symbols on macOS.
if(APPLE)
  set_target_properties(${bindings_library} PROPERTIES LINK_FLAGS "-undefined dynamic_lookup")
endif(APPLE)

# Find and link to the python import library only on Windows.
# On Linux and macOS, the undefined symbols will get resolved by the dynamic linker
# (the symbols will be picked up in the Python executable).
if (WIN32)
    list(GET python_linking_data 0 python_libdir)
    list(GET python_linking_data 1 python_lib)
    find_library(python_link_flags ${python_lib} PATHS ${python_libdir} HINTS ${python_libdir})
    target_link_libraries(${bindings_library} PRIVATE ${python_link_flags})
endif()


# ================================= Dubious deployment section ================================

set(windows_shiboken_shared_libraries)

if(WIN32)
    # =========================================================================================
    # !!! (The section below is deployment related, so in a real world application you will
    # want to take care of this properly (this is simply to eliminate errors that users usually
    # encounter.
    # =========================================================================================
    # Circumvent some "#pragma comment(lib)"s in "include/pyconfig.h" which might force to link
    # against a wrong python shared library.

    set(python_versions_list 3 36 37 38 39)
    set(python_additional_link_flags "")
    foreach(ver ${python_versions_list})
        set(python_additional_link_flags
            "${python_additional_link_flags} /NODEFAULTLIB:\"python${ver}_d.lib\"")
        set(python_additional_link_flags
            "${python_additional_link_flags} /NODEFAULTLIB:\"python${ver}.lib\"")
    endforeach()

    set_target_properties(${bindings_library}
                           PROPERTIES LINK_FLAGS "${python_additional_link_flags}")

    # Compile a list of shiboken shared libraries to be installed, so that
    # the user doesn't have to set the PATH manually to point to the PySide6 package.
    foreach(library_path ${shiboken_shared_libraries})
        string(REGEX REPLACE ".lib$" ".dll" library_path ${library_path})
        file(TO_CMAKE_PATH ${library_path} library_path)
        list(APPEND windows_shiboken_shared_libraries "${library_path}")
    endforeach()
    # =========================================================================================
    # !!! End of dubious section.
    # =========================================================================================
endif()

# =============================================================================================
# !!! (The section below is deployment related, so in a real world application you will want to
# take care of this properly with some custom script or tool).
# =============================================================================================
# Install the library and the bindings module into the source folder near the main.py file, so
# that the Python interpeter successfully imports the used module.
install(TARGETS ${bindings_library} ${library}
        LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}
        RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}
        )
install(FILES ${windows_shiboken_shared_libraries} DESTINATION ${CMAKE_CURRENT_SOURCE_DIR})
# =============================================================================================
# !!! End of dubious section.
# =============================================================================================