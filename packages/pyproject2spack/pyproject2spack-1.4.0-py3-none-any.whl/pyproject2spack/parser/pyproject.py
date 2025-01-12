"""PyProject parser.

This module parses a pyproject.toml dependencies file.
"""

import logging
import tomllib
import requests
from pathlib import Path
from typing import Optional, Dict
from packaging.specifiers import SpecifierSet

logger = logging.getLogger("parser.pyproject")


class PyProject:
    """
    Parse pyprojec.toml dependencies file to a dictionary of
    package names and version constraints.

    Methods
    -------
    dependencies
        Get package dependencies and their parsed version constraints.

    metadata
        Get package metadata including name, description, etc.

    """

    def __init__(self, filepath: Optional[Path] = None, giturl: Optional[str] = None, branch: str = "main") -> None:
        """
        Parameters
        ----------
        filepath: Optional(Path)
            Path to the pyproject.toml file, defaults to None.
        giturl: Optional(str)
            URL to the gitlab project, default to None.
        branch: Optional(str)
            Branch on which to request pyproject.toml file, defaults to "main".

        """

        logger.info("initializing PyProject object")
        self.filepath = filepath
        self.giturl = giturl
        self.content: Dict = {}

        if filepath is None and giturl is None:
            logger.error("neither a file path or a url is provided")
            raise ValueError("neither a file path or a url is provided")

        if giturl:
            logger.debug(f"provided pyproject file url: {self.giturl}")
            self.content = self._read_toml_fileurl(self.giturl, branch=branch)
        if filepath:
            logger.debug(f"provided pyproject file path: {filepath}")
            self.path = filepath
            self.content = self._read_toml_filepath(self.filepath)
        if filepath and giturl:
            logger.warning(f"both file path and file url are provided, choosing path: {self.path}")
            self.content = self._read_toml_filepath(self.filepath)

    def dependencies(self) -> Dict:
        """Parse package dependencies and the versions constraint.

        Returns
        -------
        Dict: A dictionary of dependency types and package dependencies with version cosntraints.

        """

        logger.debug("attempting to get project dependencies")
        main_deps, dev_deps, docs_deps = {}, {}, {}

        if "tool" in self.content.keys():
            _poetry_data = self.content["tool"]["poetry"]
            _raw_main_deps = _poetry_data["dependencies"]
            logger.debug("parsing main raw dependencies")
            main_deps = self._parse_raw_deps(_raw_main_deps)

            if "group" in _poetry_data.keys():
                if "dev" in _poetry_data["group"].keys():
                    _raw_dev_deps = _poetry_data["group"]["dev"]["dependencies"]
                    logger.debug("parsing dev raw dependencies")
                    dev_deps = self._parse_raw_deps(_raw_dev_deps)
                else:
                    logger.warning("found no 'dev' key in group section")

                if "docs" in _poetry_data["group"].keys():
                    _raw_docs_deps = _poetry_data["group"]["docs"]["dependencies"]
                    logger.debug("parsing docs raw dependencies")
                    docs_deps = self._parse_raw_deps(_raw_docs_deps)
                else:
                    logger.warning("found no 'docs' key in group section")
            else:
                logger.warning("found no 'group' key in poetry data section")
        else:
            logger.error("found no 'tool' key in pyproject.toml file")
            raise RuntimeError("found no 'tool' key in pyproject.toml file")

        deps = {"main": main_deps, "dev": dev_deps, "docs": docs_deps}
        return deps

    def metadata(self) -> Dict:
        metadata = {}
        _pkg_name = self.content["tool"]["poetry"]["name"]
        logger.info(f"parsing metadata for: {_pkg_name}")
        _pkg_name_list = _pkg_name.split('-')
        _pkg_name_list = [name_part.capitalize() for name_part in _pkg_name_list]
        _pkg_class_name = "Py" + ''.join(_pkg_name_list)
        logger.debug(f"set package class name to: {_pkg_class_name}")
        metadata["class_name"] = _pkg_class_name

        metadata["version"] = self.content["tool"]["poetry"]["version"]
        logger.debug(f"set package version to: {metadata['version']}")

        metadata["description"] = self.content["tool"]["poetry"]["description"]
        logger.debug(f"set package description to: {metadata['description']}")

        metadata["license"] = self.content["tool"]["poetry"]["license"]
        logger.debug(f"set license to: {metadata['license']}")

        if self.giturl:
            metadata["homepage"] = self.giturl
            logger.debug(f"set homepage to: {metadata['homepage']}")
            metadata["url"] = self.giturl + "/-/archive" + f"/{metadata['version']}" + f"/{_pkg_name}-{metadata['version']}.tar.gz"
            logger.debug(f"set package url to: {metadata['url']}")
            metadata["git"] = self.giturl
            logger.debug(f"set package git to: {metadata['git']}")
        else:
            metadata["homepage"] = "https://gitlab.com/ska-telescope/project"
            logger.warning(f"set dummy homepage to: {metadata['homepage']}")
            metadata["url"] = "https://gitlab.com/ska-telescope/archive/project-1.0.0.tar.gz"
            logger.warning(f"set dummy package url to: {metadata['url']}")
            metadata["git"] = "https://gitlab.com/ska-telescope/project"
            logger.warning(f"set dummy package git to: {metadata['git']}")

        return metadata

    def _parse_raw_deps(self, raw_deps: Dict) -> Dict:
        logger.debug("parsing raw dependencies")
        deps = {name: self._parse_toml_version_specifier(version) for name, version in raw_deps.items()}
        return deps

    def _parse_toml_version_specifier(self, version_specifier: str) -> SpecifierSet:
        logger.debug(f"parsing a SpecifierSet from toml version: {version_specifier}")
        if version_specifier.startswith('^'):
            version_specifier = f">={version_specifier[1:]}"
        logger.debug(f"assumed bound is: {version_specifier}")
        return SpecifierSet(f"{version_specifier}")

    def _read_toml_filepath(self, filepath) -> Dict:
        logger.debug(f"reading file: {filepath}")
        with open(filepath, "rb") as f:
            toml_content = tomllib.load(f)
        return toml_content

    def _read_toml_fileurl(self, giturl, branch) -> Dict:
        logger.debug(f"reading file on: {giturl}")

        if branch == "main":
            _toml_file_url = giturl + "/-/raw/main/pyproject.toml"
            logger.debug(f"perceived raw file url is: {_toml_file_url}")
        elif branch == "master":
            _toml_file_url = giturl + "/-/raw/master/pyproject.toml"
            logger.debug(f"percieved raw file url is: {_toml_file_url}")
        else:
            _toml_file_url = giturl + f"/-/raw/{branch}/pyproject.toml"
            logger.debug(f"percieved raw file url is: {_toml_file_url}")

        try:
            logger.debug(f"requesting url: {_toml_file_url}")
            response = requests.get(_toml_file_url)
        except Exception as e:
            logger.error(f"could not get a response from: {giturl}")
            logger.exception(f"{e}")
        logger.debug("loading toml data")
        toml_content = tomllib.loads(response.text)
        return toml_content
