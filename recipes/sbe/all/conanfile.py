import os
import shutil
import glob
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class SbeConan(ConanFile):
    name = "sbe"
    description = "OSI layer 6 presentation for encoding and decoding binary application messages for low-latency financial applications"
    topics = ("conan", "SBE")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/real-logic/simple-binary-encoding/wiki"
    license = "Apache-2.0"
    exports_sources = "CMakeLists.txt",
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("zulu-openjdk/11.0.8")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)

        minimal_version = {
            "Visual Studio": "16",
            "gcc": "5"
        }

        if compiler in minimal_version and compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires {} compiler {} or newer [is: {}]".format(self.name, compiler, minimal_version[compiler], compiler_version)
            )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "simple-binary-encoding-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["SBE_BUILD_SAMPLES"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "/MTd", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "/MT", "")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build(target="sbe-jar")
        cmake.build(target="ir_codecs")
        cmake.build()

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "sbe-tool/src/main/cpp")
        build_folder = os.path.join(self._source_subfolder, "sbe-all/build")

        self.copy("otf/*.h", dst="include", src=include_folder)
        self.copy("sbe/*.h", dst="include", src=include_folder)
        self.copy("uk_co_real_logic_sbe_ir_generated/*.h", dst="include", src=include_folder)

        copied_jars = self.copy("*.jar", dst="bin", src=build_folder, keep_path=False)
        for copied_jar in copied_jars:
            dirname, filename = os.path.split(copied_jar)
            noversion_filename = filename.replace('-' + self.version, '')
            if noversion_filename != filename:
                os.rename(copied_jar, os.path.join(dirname, noversion_filename))

        lib_folder = os.path.join(self._build_subfolder, "lib")
        self.copy("*.a", dst="lib", src=lib_folder)

    def package_info(self):
        includedir = os.path.join(self.package_folder, "include")
        self.cpp_info.includedirs = [includedir]

        libdir = os.path.join(self.package_folder, "lib")
        self.cpp_info.libdirs = [libdir]
        self.cpp_info.libs += self.collect_libs(libdir)

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
