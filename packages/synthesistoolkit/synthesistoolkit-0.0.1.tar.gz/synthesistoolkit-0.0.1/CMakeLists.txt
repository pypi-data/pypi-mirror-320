cmake_minimum_required(VERSION 3.30)
project(pystk)

find_package(Python
  REQUIRED COMPONENTS Interpreter Development.Module
  OPTIONAL_COMPONENTS Development.SABIModule)

execute_process(
  COMMAND "${Python3_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE nanobind_ROOT
)

find_package(nanobind CONFIG REQUIRED)

set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/stk/cmake ${CMAKE_MODULE_PATH})
set(BUILD_SHARED OFF CACHE BOOL "Whether to build the shared library" FORCE)
set(ENABLE_JACK OFF CACHE BOOL "Enable JACK" FORCE)
set(ENABLE_DS OFF CACHE BOOL "Enable DirectSound API support (windows only)" FORCE)
set(COMPILE_PROJECTS OFF CACHE BOOL "Compile all the example projects" FORCE)

add_subdirectory(stk)
set_property(TARGET stk PROPERTY POSITION_INDEPENDENT_CODE ON)

nanobind_add_module(_pystk_impl STABLE_ABI NB_STATIC
  src/instrmnt.cpp
  src/effect.cpp
  src/filter.cpp
  src/function.cpp
  src/generator.cpp
  src/pystk.cpp
)

target_compile_features(_pystk_impl PRIVATE cxx_std_17)

target_link_libraries(_pystk_impl PRIVATE stk)
target_include_directories(_pystk_impl PRIVATE stk/include)

if(WIN32)
  target_compile_definitions(stk PUBLIC -D_USE_MATH_DEFINES)
  target_compile_definitions(_pystk_impl PRIVATE -D_USE_MATH_DEFINES)
endif()

# for editable installs
file(COPY stk/rawwaves DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/src/synthesistoolkit)

install(
  TARGETS _pystk_impl LIBRARY
  DESTINATION synthesistoolkit
)

install(
  DIRECTORY stk/rawwaves
  DESTINATION synthesistoolkit
)