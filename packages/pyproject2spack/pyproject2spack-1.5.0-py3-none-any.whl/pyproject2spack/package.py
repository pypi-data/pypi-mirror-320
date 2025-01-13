# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class PySkaSdpInstrumentalCalibration(PythonPackage):
    "SKA Instrumental Calibration Pipeline"

    homepage = "https://gitlab.com/ska-telescope/project"
    url = "https://gitlab.com/ska-telescope/archive/project-1.0.0.tar.gz"
    git = "https://gitlab.com/ska-telescope/project"

    # TODO: populate maintainers as needed
    # maintainers("saliei")

    license("BSD-3-Clause")

    version("develop-0.1.4", branch="main", preferred=True)

    depends_on("python@3.10.0:", type=("build", "run"))
    depends_on("py-astropy@6.1.0:", type=("build", "run"))
    depends_on("everybeam@0.6.1:", type=("build", "run"))
    depends_on("py-nbmake@1.4.1:", type=("build", "run"))
    depends_on("py-isort@5.9.1:", type=("build", "run"))
    depends_on("py-numpy@1.26.0:", type=("build", "run"))
    depends_on("py-setuptools-scm@7.1.0:", type=("build", "run"))
    depends_on("py-jsonschema@4.18.6:", type=("build", "run"))
    depends_on("py-matplotlib@3.9.1:", type=("build", "run"))
    depends_on("py-ska-sdp-datamodels@0.3.3:", type=("build", "run"))
    depends_on("py-ska-sdp-func@1.2.0:", type=("build", "run"))
    depends_on("py-ska-sdp-func-python@0.5.1:", type=("build", "run"))
    depends_on("py-xarray@2024.7.0:", type=("build", "run"))
    depends_on("py-referencing@0.35.1:", type=("build", "run"))
    # WARNING: for the following packages no available spack 
    # version could satisfy the pyproject.toml constraint.
    depends_on("py-distributed", type=("build", "run"))
    depends_on("py-nbqa", type=("build", "run"))
    depends_on("py-flake8", type=("build", "run"))
    depends_on("py-black", type=("build", "run"))
    depends_on("py-pytest-cov", type=("build", "run"))
    depends_on("py-pylint", type=("build", "run"))
    depends_on("py-recommonmark", type=("build", "run"))
    depends_on("py-attrs", type=("build", "run"))
    depends_on("py-rpds-py", type=("build", "run"))
    depends_on("py-jsonschema-specifications", type=("build", "run"))
    # TODO: for the following packages no spack package could be found.
    #depends_on("py-pytest-json-report@1.5.0:", type=("build", "run"))
    #depends_on("py-pytest-json@0.4.0:", type=("build", "run"))
    #depends_on("py-python-casacore@3.5:", type=("build", "run"))
    #depends_on("py-pylance@0.5.9:", type=("build", "run"))
    
    variant("dev", default=False, description="Install development dependencies.")
    depends_on("py-markupsafe@2.1.3:", type=("build", "run"))
    depends_on("py-pygments@2.15.1:", type=("build", "run"))
    depends_on("py-pytest-pylint@0.21.0:", type=("build", "run"))
    depends_on("py-python-dotenv@0.19.2:", type=("build", "run"))
    depends_on("py-setuptools@68.0.0:", type=("build", "run"))
    depends_on("py-pipdeptree@2.13.0:", type=("build", "run"))
    # WARNING: for the following packages no available spack 
    # version could satisfy the pyproject.toml constraint 
    depends_on("py-docutils", type=("build", "run"))
    depends_on("py-pylint", type=("build", "run"))
    depends_on("py-pytest", type=("build", "run"))
    depends_on("py-pytest-cov", type=("build", "run"))
    # TODO: for the following packages no spack package could be found.
    #depends_on("py-pylint-junit@0.3.2:", type=("build", "run"))
    
    variant("docs", default=False, description="Install documentation dependencies.")
    depends_on("py-sphinx@8.1.0:", type=("build", "run"))
    depends_on("py-numpy@1.26.0:", type=("build", "run"))
    depends_on("py-ska-sdp-datamodels@0.3.3:", type=("build", "run"))
    depends_on("py-ska-sdp-func-python@0.5.1:", type=("build", "run"))
    depends_on("py-xarray@2024.7.0:", type=("build", "run"))
    depends_on("everybeam@0.6.1:", type=("build", "run"))
    # WARNING: for the following packages no available spack 
    # version could satisfy the pyproject.toml constraint.
    depends_on("py-sphinx-autodoc-typehints", type=("build", "run"))
    depends_on("py-sphinx-rtd-theme", type=("build", "run"))
    depends_on("py-sphinxcontrib-websupport", type=("build", "run"))
    depends_on("py-recommonmark", type=("build", "run"))
    # TODO: for the following packages no spack package could be found.
    #depends_on("py-sphinx-autobuild@2021.3.14:", type=("build", "run"))
    
    def setup_build_environment(self, env):
        env.set("POETRY_SOURCE_AUTH_SKAO", '')
        env.set("POETRY_REPOSITORIES_SKAO_URL", "")

    def install(self, spec, prefix):
        poetry = which("poetry")
        poetry("config", "virtualenvs.create", "false")
        poetry("install", "--no-dev", "--no-interaction")
        
        if "+dev" in spec:
            poetry("install", "--with", "dev", "--no-interaction")
        if "+docs" in spec:
            poetry("install", "--with", "docs", "--no-interaction")
        
        super().install(spec, prefix)

    def build_args(self, spec, prefix):
        return ["--no-deps"]

    @property
    @llnl.util.lang.memoized
    def _output_version(self):
        spec_vers_str = str(self.spec.version.up_to(3))
        if "develop" in spec_vers_str:
            # Remove "develop-" from the version in spack
            spec_vers_str = spec_vers_str.partition('-')[2]
        return spec_vers_str