cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Java REQUIRED Runtime)

set(CODEC_TARGET_DIR ${CMAKE_BINARY_DIR}/codecs)
set(GENERATED_CODECS ${CODEC_TARGET_DIR}/baseline)
set(CODEC_EXAMPLES_SCHEMA_DIR ${CMAKE_SOURCE_DIR}/schema)
set(SBE_JAR ${CONAN_BIN_DIRS_SBE}/sbe-all.jar)
set(EXAMPLES_SCHEMA ${CODEC_EXAMPLES_SCHEMA_DIR}/example-schema.xml)
add_custom_command(
    OUTPUT ${GENERATED_CODECS}
    WORKING_DIRECTORY ${CODEC_EXAMPLES_SCHEMA_DIR}
    COMMAND ${Java_JAVA_EXECUTABLE} -Dsbe.output.dir=${CODEC_TARGET_DIR} -Dsbe.generate.ir=true -Dsbe.target.language=cpp -Dsbe.xinclude.aware=true -jar ${SBE_JAR} ${EXAMPLES_SCHEMA}
)
add_custom_target(examples_codecs DEPENDS ${GENERATED_CODECS})

include_directories(${CODEC_TARGET_DIR})
add_executable(GeneratedStubExample GeneratedStubExample.cpp)
add_executable(OtfExample OtfExample.cpp)
target_link_libraries(OtfExample ${CONAN_LIBS})

add_dependencies(GeneratedStubExample examples_codecs)
add_dependencies(OtfExample examples_codecs)

#add_executable(${PROJECT_NAME} test_package.cpp)
#target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
