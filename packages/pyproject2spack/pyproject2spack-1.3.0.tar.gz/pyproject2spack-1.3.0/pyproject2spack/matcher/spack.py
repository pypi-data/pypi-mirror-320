"""Spack matcher.

This module matches given packages and version constraints with Spack databases.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from packaging.version import Version

logger = logging.getLogger("matcher.spack")


class Spack:
    """
    Match given packages with version constraints with that of available packages
        in Spack repositories.

    Methods
    -------
    match
        Matches given constraints to that of Spack database.

    match_single_type(dep_type: str)
        Matches given constraints of a single dependency type, e.g. dev,
            to that of Spack database.
    """

    def __init__(self, constraints: Dict,
                 dbpath: Optional[Path] = Path("./spackdb.json"),
                 updatedb: Optional[bool] = False) -> None:
        """
        Parameters
        ----------
        constraints: Dict
            Given package names and version constraints to be matched.

        dbpath: Optional[Path]
            Path to Spack json database, defaults to "./spackdb.json"

        updatedb: Optional[book]
            Wether to update the Spack database or not, defaults to False.
        """

        logger.info(f"initializing spack matcher, database path: {dbpath}, updatedb: {updatedb}")
        self.constraints: Dict = constraints
        self.dbpath: Optional[Path] = dbpath
        self.db: Dict = {}
        if updatedb:
            self._updatedb()
            self.db = self._loaddb()
        else:
            self.db = self._loaddb()
        self.names: List[str] = self._pkg_names()
        self.matches: Dict = {}

    def match(self) -> Dict:
        """Match given constraints to that of Spack databse.

        Returns
        -------
        matches: Dict
            Matched Spack packages with appropraite constraints.
        """

        logger.debug("matching constraints")
        dep_types = self.constraints.keys()
        logger.debug(f"received dependency types of: {list(dep_types)}")
        for dep_type in dep_types:
            self.matches[dep_type] = self.match_single_type(dep_type)

        logger.debug("extracting unique main dependencies")
        _main_matches_names = set()
        if "main" in dep_types:
            logger.debug("assuming main dependency section name: 'main'")
            _main_matches = self.matches["main"]
            for match_type in _main_matches.keys():
                for pkg in _main_matches[match_type]:
                    _main_matches_names.update(pkg["name"])

        for dep_type in dep_types:
            logger.debug(f"checking for duplicate packages in dependency section: {dep_type}")
            if dep_type != "main":
                for match_type in self.matches[dep_type].keys():
                    for idx, pkg in enumerate(self.matches[dep_type][match_type]):
                        if pkg["name"] in _main_matches_names:
                            logger.warning(f"found duplicate dependency: {pkg['name']}")
                            del self.matches[dep_type][match_type][idx]
                            logger.warning(f"deleted duplicate dependency: {pkg['name']}")
        return self.matches

    def match_single_type(self, dep_type: str) -> Dict:
        """"Matches given constraints of a single dependency type, e.g. dev,
            to that of Spack database.

        Parameters
        ----------
        dep_type: str
            Dependency type of given constraint, e.g. dev.

        Raise
        -----
        RuntimeError
            If the dependency type could not be found in the given constraint dictionary keys.
        """

        logger.debug(f"launching single dependency type matcher for: {dep_type}")
        if dep_type in self.constraints.keys():
            logger.debug(f"attempting to match constraints for dependency type: {dep_type}")
        else:
            logger.error(f"could not find dependency type in the given constraints: {dep_type}")
            raise RuntimeError(f"could not find dependency type in the given constraints: {dep_type}")

        matches = {}
        matches["constraint_found"] = []
        matches["constraint_not_found"] = []
        matches["package_not_found"] = []

        for given_name in self.constraints[dep_type].keys():
            name = self._equivalen_name(given_name)
            given_constraint = self.constraints[dep_type][given_name]
            logger.debug(f"received constraint for package, {given_name}: {given_constraint}")

            logger.debug(f"matching constraint for package: {name}")
            match_dict = {"name": name, "version": None, "latest_version": None, "versions_string_values": []}
            if name not in self.names:
                logger.warning(f"package not found in Spack database: {name}")
                match_dict["version"] = given_constraint
                matches["package_not_found"].append(match_dict)
                logger.warning(f"set matched version constraint to the received one, {name}: {given_constraint}")
                continue
            else:
                for pkg in self.db:
                    if pkg["name"] == name:
                        logger.debug(f"found package in Spack database: {name}")
                        if "latest_version" in pkg.keys():
                            match_dict["latest_version"] = Version(pkg["latest_version"])
                            logger.info(f"latest version for package, {name}: {match_dict['latest_version']}")

                        if "versions" in pkg.keys():
                            if "latest" in pkg["versions"]:
                                match_dict["versions_string_values"].append("latest")
                                logger.warning(f"versions list has string, {name}: 'latest'")
                            if "develop" in pkg["versions"]:
                                match_dict["versions_string_values"].append("develop")
                                logger.warning(f"versions list has string, {name}: 'develop'")
                            if "main" in pkg["versions"]:
                                match_dict["versions_string_values"].append("main")
                                logger.warning(f"versions list has string, {name}: 'main'")
                            for version_string_value in match_dict["versions_string_values"]:
                                logger.warning(f"removing string version values from available versions for: {name}")
                                pkg["versions"].remove(version_string_value)

                            available_versions = [Version(f"{v}") for v in pkg["versions"]]
                            satisfying_versions = [v for v in available_versions if v in self.constraints[dep_type][given_name]]
                            if satisfying_versions:
                                closest_version = min(satisfying_versions)
                                logger.debug(f"setting closest satisfying version, {name}: {closest_version}")
                                match_dict["version"] = closest_version
                                matches["constraint_found"].append(match_dict)
                            else:
                                match_dict["version"] = given_constraint
                                logger.warning(f"matching constraint could not be found for: {name}")
                                matches["constraint_not_found"].append(match_dict)
                                logger.warning(f"set matched version constraint to the received one, {name}: {given_constraint}")
        return matches

    def _equivalen_name(self, name) -> None:
        """Given a package name deduce an equivalent Spack package name."""

        logger.debug(f"generating equivalent Spack package name for: {name}")
        rep_name = name.replace('_', '-')
        spack_name = "py-" + rep_name
        if name == "everybeam":
            spack_name = "everybeam"
        if name == "python":
            spack_name = "python"
        logger.debug(f"deduced Spack package name for, {name}: {spack_name}")
        return spack_name

    def _updatedb(self) -> None:
        """Update Spack package database file."""

        cmd = ["spack", "list", "--format=version_json"]
        logger.debug(f"attempting to update spack packages database with: {cmd}")
        try:
            result = subprocess.run(cmd, capture_output=True, check=True, text=True)
            data = json.loads(result.stdout)
            logger.debug(f"captured output from command: {cmd}")
        except subprocess.CalledProcessError as e:
            logger.exception(f"error running command: {cmd}")
            logger.error(f"stderr: {e.stderr}")
        except json.JSONDecodeError:
            logger.exception(f"could not decode json output from command: {cmd}")

        try:
            with open(self.dbpath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.exception(f"exceptions occured when attempting to wite to file: {self.dbpath}")

    def _loaddb(self) -> Dict:
        """Load Spack database file."""

        logger.debug("loading spack database json file")
        try:
            with open(self.dbpath, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.exception(f"could not load spack database file: {self.dbpath}")
        except json.JSONDecodeError:
            logger.exception(f"could not decode json content from file: {self.dbpath}")
        return data

    def _pkg_names(self) -> List[str]:
        """Extract package names from Spack database."""

        logger.info("extracting package names from Spack database file")
        names = [pkg["name"] for pkg in self.db]
        return names
