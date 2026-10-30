.. SPDX-FileCopyrightText: 2020-2026 Intel Corporation
..
.. SPDX-License-Identifier: MIT

==================
oneapi-spack-tests
==================

.. image:: https://github.com/rscohn2/oneapi-spack-tests/workflows/.github/workflows/ci.yml/badge.svg
   :target: https://github.com/rscohn2/oneapi-spack-tests/actions?query=workflow%3A.github%2Fworkflows%2Fci.yml

.. image:: https://api.reuse.software/badge/github.com/rscohn2/oneapi-spack-tests
   :target: https://api.reuse.software/info/github.com/rscohn2/oneapi-spack-tests
   :alt: REUSE status

The files here test oneapi support in spack. It installs compilers,
and uses icpc/icpx/ifort/ifx/g++/gfortran to build programs that use
the oneapi libraries and SYCL. It uses a sample package that contains
programs that use oneAPI components.

It tests the following:

* intel-oneapi-* packages as dependencies
* include directories are accessible
* library directories are accessible
* packages provide correct configuration when used as a virtual
  provider
* environment variables are set

Install prerequisites for testing::

  pip install -r requirements.txt

Setup tests::

  # Install and activate spack
  git clone https://github.com/spack/spack.git
  source spack/share/spack/setup-env.sh
  # Optionally use a local clone of the builtin packages
  # (https://github.com/spack/spack-packages)
  spack repo set --destination /path/to/local/spack-packages builtin
  # Add the test packages
  spack repo add ./repo/spack_repo/oneapi_test
  # Install and activate compilers
  spack install intel-oneapi-compilers
  spack compiler add `spack location -i intel-oneapi-compilers`/compiler/latest/linux/bin/intel64
  spack compiler add `spack location -i intel-oneapi-compilers`/compiler/latest/linux/bin

Run all tests::

  pytest -s tests

Run pre-commit checks::

  pre-commit run --all

The sample applications are in the samples_ directory. The spack
package that downloads/builds/installs the sample applications is in
the repo_ directory.

Adding samples
==============

Add to samples_, `package.py`_, and `test_packages.py`_.

Adding to CI
============

We divided the tests into groups because GitHub Actions runners do not
have enough disk space to install all of oneAPI.

.. _samples: samples
.. _repo: repo
.. _`package.py`: repo/packages/oneapi-test-basic/package.py
.. _`test_packages.py`: tests/test_packages.py
