cmake_minimum_required(VERSION 3.15)
project(simple_ans)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(DEFINED ENV{PYODIDE})
    # Pyodide/Emscripten build
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -O3")
    set(PYBIND11_FINDPYTHON OFF)
else()
    # Native build
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -O3")
endif()

find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_simple_ans
    simple_ans_bind.cpp
    simple_ans/cpp/simple_ans.cpp
)

target_include_directories(_simple_ans PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/simple_ans/cpp
)

install(TARGETS _simple_ans DESTINATION simple_ans)
