# SPDX-FileCopyrightText: 2026 Intel Corporation
#
# SPDX-License-Identifier: MIT

from pathlib import Path
from types import SimpleNamespace

import pytest
import test_packages

spack_repo = pytest.importorskip('spack.repo')
spack_spec = pytest.importorskip('spack.spec')
spack_deptypes = pytest.importorskip('spack.deptypes')


@pytest.mark.parametrize(
    'test_function,sample',
    [
        (getattr(test_packages, f'test_icx_{group}'), sample)
        for group in (1, 2, 3)
        for sample in getattr(test_packages, f'icx{group}_samples')
    ],
)
def test_icx_sample_variant_scope(monkeypatch, test_function, sample):
    requests = []
    monkeypatch.setattr(test_packages, 'spack_install', requests.append)
    test_function(clean=None, sample=sample)
    assert len(requests) == 1
    spec = spack_spec.Spec(requests[0])
    assert spec.name == 'oneapi-test-basic'
    assert f'+{sample}' in spec
    compiler = spec['intel-oneapi-compilers']
    assert not compiler.variants


@pytest.mark.parametrize(
    'component,virtual',
    [
        ('mkl', False),
        ('mpi', False),
        ('mkl', True),
        ('mpi', True),
        ('scalapack', True),
    ],
)
def test_install_dependency_lookup(monkeypatch, component, virtual):
    root = Path(__file__).parents[1]
    with spack_repo.use_repositories(
        str(root / 'repo/spack_repo/oneapi_test'), override=False
    ) as repos:
        cls = repos.get_pkg_class('oneapi-test-basic')
        spec = spack_spec.Spec(
            f'oneapi-test-basic +{component} '
            + ('+virtual' if virtual else '~virtual')
        )
        name = component if virtual else f'intel-oneapi-{component}'
        provider = 'mkl' if component == 'scalapack' else component
        dependency = spack_spec.Spec(f'intel-oneapi-{provider}')
        spec.add_dependency_edge(
            dependency,
            depflag=spack_deptypes.LINK,
            virtuals=(component,) if virtual else (),
        )
        assert spec[name] is dependency
        dependency.set_prefix('/dependency')
        dependency._mark_concrete()
        monkeypatch.setattr(
            spack_spec.Spec,
            'libs',
            property(lambda self: SimpleNamespace(ld_flags='-ltest')),
        )
        calls = []
        monkeypatch.setattr(
            cls.module, 'make', lambda *args: calls.append(args), raising=False
        )
        pkg = cls.__new__(cls)
        pkg.spec = spec
        pkg.install(spec, '/install')

        assert len(calls) == 1
        assert f'{component.upper()}_LD_FLAGS=-ltest' in calls[0]
        assert f'{component}-sample.out' in calls[0]
        if component == 'mpi':
            assert 'MPI_PREFIX=/dependency/mpi/latest' in calls[0]
