# pyproject2spack

This project consists of 4 modules, a modified `logger` from python's builtin logger module, 
a `matcher` module, for now only a `spack` matcher, a `parser` module, for now only a `pyproject` parser, 
and a `renderer` module, a Jinja2 renderer. 

In theory by adding a custom parser and a matcher this can convert arbitrary 
projects to one another. 

# Installation

You can simply clone the repository and use the `pyproject2spack.py` script or import the modules:
```bash
git clone https://gitlab.com/saliei/pyproject2spack
cd pyproject2spack
./pyproject2spack.py --log-max-lines=10 --log-delay=0.01 --gitlab-url=<URL>
```

Or install the package from PyPI registry using pip:
```bash
pip install pyproject2spack
```

# Usage

The workflow is intuitive:
```python
from pyproject2spack.parser.pyproject import PyProject
from pyproject2spack.matcher.spack import Spack
from pyproject2spack.renderer.jinja2 import Renderer

# parse pyproject.toml file
prj = PyProject(giturl=gitlab_url)
constraints = prj.dependencies()
metadata = prj.metadata()

# match version constraints to that of spack database
matcher = Spack(constraints=constraints)
matches = matcher.match()

# render a template given template variables
renderer = Renderer(matches=matches, metadata=metadata)
renderer.render()
```

Apart from using as a module there is also an executable helper script, [pyproject2spack.py](./pyproject2spack/pyproject2spack.py) 
for converting a `pyproject.toml` based python projects to spack `package.py`:
```text
pyproject2spack.py --help
usage: pyproject2spack [-h] [--no-log] [--log-max-lines LOG_MAX_LINES] [--log-delay LOG_DELAY] 
                       [--update-spackdb] --gitlab-url [GITLAB_URL] [--dbpath [DBPATH]] 
                       [--templates-dir [TEMPLATES_DIR]] [--template-name [TEMPLATE_NAME]]
                       [--output [OUTPUT]]

Convert pyproject.toml python package to spack python package.

options:
  -h, --help            show this help message and exit
  --no-log              wether to print log messages or not
  --log-max-lines LOG_MAX_LINES
                        number of fixed lines in the logger output, default is 0, 
                        the normal behaviour
  --log-delay LOG_DELAY
                        the delay between log messages in seconds, default is 0
  --gitlab-url [GITLAB_URL]
                        URL of python project's gitlab repo (required)
  --update-spackdb      wether to update the spack json database file or not
  --dbpath [DBPATH]     path to spack database json file
  --templates-dir [TEMPLATES_DIR]
                        path to jinja2 templates dir
  --template-name [TEMPLATE_NAME]
                        template name to be rendered
  --output [OUTPUT]     rendered output file path

Square Kilometre Array Observatory (SKAO)
```

# Note
The generated package should be examined and tested thoroughly. This utility package provides no guarantee.
