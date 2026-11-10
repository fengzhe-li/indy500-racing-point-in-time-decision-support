cmake_minimum_required(VERSION 3.16)
project(indy500_pit_cpp VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

option(INDY500_BUILD_TESTS "Build C++ unit tests" ON)
option(INDY500_BUILD_PYTHON "Build pybind11 Python extension" ON)

add_library(indy500_pit_engine STATIC
    src/pit_engine.cpp
)

target_include_directories(indy500_pit_engine PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

if(MSVC)
    target_compile_options(indy500_pit_engine PRIVATE /W4)
else()
    target_compile_options(indy500_pit_engine PRIVATE -Wall -Wextra -Wpedantic)
endif()

if(INDY500_BUILD_TESTS)
    enable_testing()
    find_package(GTest QUIET)
    if(NOT GTest_FOUND)
        include(FetchContent)
        FetchContent_Declare(
            googletest
            URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
            DOWNLOAD_EXTRACT_TIMESTAMP TRUE
        )
        set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
        FetchContent_MakeAvailable(googletest)
    endif()

    add_executable(indy500_pit_tests
        tests/test_pit_engine.cpp
    )
    target_link_libraries(indy500_pit_tests PRIVATE
        indy500_pit_engine
        GTest::gtest_main
    )
    target_compile_definitions(indy500_pit_tests PRIVATE
        INDY500_REPO_ROOT="${CMAKE_CURRENT_SOURCE_DIR}/.."
    )

    include(GoogleTest)
    gtest_discover_tests(indy500_pit_tests)
endif()

if(INDY500_BUILD_PYTHON)
    find_package(Python3 COMPONENTS Interpreter Development.Module QUIET)
    find_package(pybind11 CONFIG QUIET)
    if(NOT pybind11_FOUND AND Python3_Interpreter_FOUND)
        execute_process(
            COMMAND "${Python3_EXECUTABLE}" -m pybind11 --cmakedir
            OUTPUT_VARIABLE _pybind11_cmake_dir
            OUTPUT_STRIP_TRAILING_WHITESPACE
            RESULT_VARIABLE _pybind11_res
            ERROR_QUIET
        )
        if(_pybind11_res EQUAL 0 AND EXISTS "${_pybind11_cmake_dir}")
            list(APPEND CMAKE_PREFIX_PATH "${_pybind11_cmake_dir}")
            find_package(pybind11 CONFIG QUIET)
        endif()
    endif()

    if(pybind11_FOUND)
        pybind11_add_module(_indy500_pit_cpp bindings/pybind_module.cpp)
        target_link_libraries(_indy500_pit_cpp PRIVATE indy500_pit_engine)
        set_target_properties(_indy500_pit_cpp PROPERTIES
            LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/python"
        )
    else()
        message(STATUS "pybind11 not found; skipping Python extension build (_indy500_pit_cpp)")
    endif()
endif()
