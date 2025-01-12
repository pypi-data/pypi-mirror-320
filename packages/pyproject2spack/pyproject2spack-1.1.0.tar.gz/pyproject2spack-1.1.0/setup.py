from setuptools import setup, find_packages

with open("README.md", 'r', encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", 'r', encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name="pyproject2spack",
    version="1.1.0",
    author="Saeid Aliei",
    author_email="saeidaliei@gmail.com",
    description="Convert Python projects to Spack packages",
    long_description="Convert pyproject.toml based python packages to Spack packages. \
    At it's core this package provides 4 modules, a logger, \
    a matcher (spack), a renderer (jinja2), and a parser (pyproject). \
    These can be extended to convert arbitrary form of packages to one another.",
    long_description_content_type="text/markdown",
    url="https://gitlab.com/saliei/pyproject2spack",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        'pyproject2spack': ['templates/*'],
    },
    entry_points={
        'console_scripts': [
            'pyproject2spack=pyproject2spack.pyproject2spack:main',
        ],
    },
)
