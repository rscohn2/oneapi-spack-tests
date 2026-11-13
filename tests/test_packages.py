# SPDX-FileCopyrightText: 2020-2026 Intel Corporation
#
# SPDX-License-Identifier: MIT

import os
import subprocess

import pytest


def shell(cmd, check=True, capture_output=False, modify=False):
    print(cmd)
    return subprocess.run(
        cmd, shell=True, check=check, capture_output=capture_output
    )


def spack_install(options):
    # checksums are not right because source is in this
    # repo. fail-fast is needed to make spack return a non zero error
    # code when a dependency fails
    shell(f'spack install --fail-fast {options}')
    # github actions have limited space, so delete cached downloads
    if 'GITHUB_WORKFLOW' in os.environ:
        shell('spack clean --downloads')
        shell('df -h .')


# Split into separate lists because github actions runners have
# limited disk space
icx1_samples = [
    'cpp',
    'fortran',
    'sycl',
    'mkl',
    'dnn',
    'dpl',
]

icx2_samples = [
    'dal',
    'vpl',
]

icx3_samples = [
    'ipp',
    'ippcp',
    'mpi',
    'tbb',
]


@pytest.mark.parametrize('sample', icx1_samples)
def test_icx_1(clean, sample):
    spack_install(f'oneapi-test-basic +{sample} %oneapi')


@pytest.mark.parametrize('sample', icx2_samples)
def test_icx_2(clean, sample):
    spack_install(f'oneapi-test-basic +{sample} %oneapi')


@pytest.mark.parametrize('sample', icx3_samples)
def test_icx_3(clean, sample):
    spack_install(f'oneapi-test-basic +{sample} %oneapi')


def test_external_libfabric(clean):
    spack_install('oneapi-test-basic +mpi +external-libfabric')


# ilp64 variants
ilp64_components = [
    'mkl',
    'mpi',
]


@pytest.mark.parametrize('component', ilp64_components)
def test_ilp64(clean, component):
    spack_install(f'oneapi-test-basic +ilp64 +{component}')


virtual_packages = ['tbb', 'mkl', 'mpi', 'scalapack']


@pytest.mark.parametrize('package', virtual_packages)
def test_virtual(clean, package):
    if package == 'scalapack':
        spack_install(
            (
                'oneapi-test-basic +virtual +scalapack'
                ' ^intel-oneapi-mkl +cluster -shared ^intel-oneapi-mpi'
            )
        )
    else:
        spack_install(
            (
                f'oneapi-test-basic +virtual +{package}'
                f' ^intel-oneapi-{package}'
            )
        )


# build with gcc
gcc1_samples = [
    'cpp',
    'fortran',
    'dal',
    'mkl',
    'mpi',
    'tbb',
]

gcc2_samples = [
    'ipp',
    'ippcp',
    'vpl',
]


@pytest.mark.parametrize('sample', gcc1_samples)
def test_gcc_1(clean, sample):
    if sample == 'mpi':
        spack_install('oneapi-test-basic +mpi +external-libfabric')
    spack_install(f'oneapi-test-basic +{sample}')


@pytest.mark.parametrize('sample', gcc2_samples)
def test_gcc_2(clean, sample):
    spack_install(f'oneapi-test-basic +{sample}')


@pytest.mark.parametrize('component', ['tbb'])
def test_load(component):
    package = f'intel-oneapi-{component}'
    out_file = f'{component}-sample.out'
    spack_install(f'{package}')
    shell(
        '. spack/share/spack/setup-env.sh && '
        f'spack load {package} && '
        f'make -C samples {out_file}'
    )
