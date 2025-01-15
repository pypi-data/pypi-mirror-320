# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Windninja(CMakePackage):
    """WindNinja is a diagnostic wind model developed for use in wildland fire modeling."""

    url = "https://github.com/firelab/windninja/archive/refs/tags/3.10.0.tar.gz"
    git = "https://github.com/firelab/windninja"
 
    maintainers("Chrismarsh")

    # rebranded NIST fallback license
    # https://github.com/firelab/windninja/blob/master/LICENSE
    license("NIST-PD-fallback")

    version("3.10.0", sha256="7ab120c7465afbe5e95e5eec32523a41ff010094c9b2db87cf9ac4b8eac1f956")

    variant("openmp", default=True, description="Enable OpenMP support")
    variant("ninjafoam", default=False, description="Enable OpenFoam support")
    variant("qtgui", default=False, description="Build Qt GUI")

    variant("build_fetch_dem", default=False, description="Build a standalone command line interface DEM utility")
    variant("build_stl_converter", default=False, description="Build a standalone command line interface for STL file conversions")
    variant("build_convert_output", default=False, description="Build a standalone command line interface for xyz file conversions")
    variant("build_solar_grid", default=False, description="Build a application for building solar grids")

    depends_on("cmake@3.0:",type="build")
    depends_on("boost@1.74.0: +date_time +program_options +test")
    depends_on("gdal@3.4.1: +netcdf +curl")
    depends_on("llvm-openmp", when="%apple-clang +openmp")
    depends_on("openfoam", when="+ninjafoam")

    depends_on("qt@4", when="+qtgui")

    conflicts(
        "+ninjafoam",
        when="platform=darwin",
        msg="ninjafoam is not supported on Macos because OpenFoam does not build on Macos",
    )

    def cmake_args(self):

        args = [

            self.define("NINJA_QTGUI", False),
            self.define("NINJAFOAM", False),
            self.define("CMAKE_CXX_STANDARD", "11"),
            self.define_from_variant("OPENMP_SUPPORT", "openmp"),
            self.define_from_variant("NINJAFOAM", "ninjafoam"),
            self.define_from_variant("NINJA_QTGUI", "qtgui"),
            self.define_from_variant("BUILD_FETCH_DEM", "build_fetch_dem"),
            self.define_from_variant("BUILD_STL_CONVERTER", "build_stl_converter"),
            self.define_from_variant("BUILD_CONVERT_OUTPUT", "build_convert_output"),
            self.define_from_variant("BUILD_SOLAR_GRID", "build_solar_grid"),

        ]
        return args


    @when("%apple-clang +openmp")
    def patch(self):
        # WN needs to link against openmp explicitly when using apple-clang
        cmake_files = find(self.stage.source_path, "CMakeLists.txt", recursive=True)
        filter_file(r"set\(LINK_LIBS", "set(LINK_LIBS OpenMP::OpenMP_CXX ", *cmake_files, ignore_absent=True)

