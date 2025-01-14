""" Compile script for Fortran """

import os
import subprocess
import sys
from pathlib import Path

import numpy as np

DEFAULT_FC = "gfortran"

f90_modules = {
    "representations/frepresentations": ["frepresentations.f90"],
    "representations/facsf": ["facsf.f90"],
    "representations/fslatm": ["fslatm.f90"],
    "representations/arad/farad_kernels": ["farad_kernels.f90"],
    "representations/fchl/ffchl_module": [
        "ffchl_kernel_types.f90",
        "ffchl_module.f90",
        "ffchl_module_ef.f90",
        "ffchl_kernels.f90",
        "ffchl_scalar_kernels.f90",
        "ffchl_kernels_ef.f90",
        "ffchl_force_kernels.f90",
    ],
    "solvers/fsolvers": ["fsolvers.f90"],
    "kernels/fdistance": ["fdistance.f90"],
    "kernels/fkernels": [
        "fkernels.f90",
        "fkpca.f90",
        "fkwasserstein.f90",
    ],
    "kernels/fgradient_kernels": ["fgradient_kernels.f90"],
    "utils/fsettings": ["fsettings.f90"],
}


def find_mkl():
    raise NotImplementedError()


def find_env() -> dict[str, str]:
    """Find compiler flag"""

    """
    For anaconda-like envs
        TODO Find MKL

    For brew,

        brew install llvm libomp
        brew install openblas lapack

        export LDFLAGS="-L/opt/homebrew/opt/lapack/lib"
        export CPPFLAGS="-I/opt/homebrew/opt/lapack/include"
        export LDFLAGS="-L/opt/homebrew/opt/libomp/lib"
        export CPPFLAGS="-I/opt/homebrew/opt/libomp/include"

    """

    fc = os.environ.get("FC", DEFAULT_FC)

    # TODO Check if FC is there, not not raise Error
    # TODO Check if lapack / blas is there, if not raise Error
    # TODO Check if omp is installed

    # TODO Find ifort flags, choose from FC
    # TODO Find mkl lib

    # TODO Check if darwin, check for brew paths

    # Default GNU flags
    compiler_flags = [
        "-O3",
        "-m64",
        "-march=native",
        "-fPIC",
        "-Wno-maybe-uninitialized",
        "-Wno-unused-function",
        "-Wno-cpp",
    ]
    compiler_openmp = [
        "-fopenmp",
    ]
    linker_flags = [
        "-lpthread",
        "-lm",
        "-ldl",
    ]
    linker_openmp = [
        "-lgomp",
    ]
    linker_math = [
        "-lblas",
        "-llapack",
        "-L/usr/lib/",
    ]

    # MacOS X specific flags
    if "darwin" in sys.platform:

        expected_omp_dir = Path("/opt/homebrew/opt/libomp/lib")

        if expected_omp_dir.is_dir():
            compiler_openmp = [
                "-fopenmp",
            ]
            linker_openmp = [
                f"-L{expected_omp_dir}",
                "-lomp",
            ]

        else:
            print(f"Expected OpenMP dir not found: {expected_omp_dir}, compiling without OpenMP")
            compiler_openmp = []
            linker_openmp = []

    # FreeBSD specific flags
    if "freebsd" in sys.platform:
        # Location of BLAS / Lapack for FreeBSD 14
        linker_math += ["-L/usr/local/lib/"]

    fflags = [] + compiler_flags + compiler_openmp
    ldflags = [] + linker_flags + linker_math + linker_openmp

    env = {"FFLAGS": " ".join(fflags), "LDFLAGS": " ".join(ldflags), "FC": fc}

    return env


def main():
    """Compile f90 in src/qmllib"""

    print(
        f"Using python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    print(f"Using numpy {np.__version__}")

    # Find and set Fortran compiler, compiler flags and linker flags
    env = find_env()
    for key, value in env.items():
        print(f"export {key}='{value}'")
        os.environ[key] = value

    f2py = [sys.executable, "-m", "numpy.f2py"]

    meson_flags = [
        "--backend",
        "meson",
    ]

    for module_name, module_sources in f90_modules.items():

        path = Path(module_name)
        parent = path.parent
        stem = path.stem

        cwd = Path("src/qmllib") / parent
        cmd = f2py + ["-c"] + module_sources + ["-m", str(stem)] + meson_flags
        print(cwd, " ".join(cmd))

        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        stdout = proc.stdout
        stderr = proc.stderr
        exitcode = proc.returncode

        if exitcode > 0:
            print(stderr)
            print()
            print(stdout)
            exit(exitcode)


if __name__ == "__main__":
    main()
