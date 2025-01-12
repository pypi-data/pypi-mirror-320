"""Renderer wrapper for Jinja2 templates.

This module renders a Jinja2 template given template variables.
"""

import re
import logging
import jinja2
from pathlib import Path
from typing import Optional, Dict
from packaging.version import Version
from packaging.specifiers import SpecifierSet


logger = logging.getLogger("renderer.renderer")


class Renderer:
    """This class renders a template given template variables including version matches.

    Methods
    -------
    render:
        Renders a template with version matches and package metadata information.
    """

    def __init__(self, matches: Dict,
                 metadata: Dict,
                 templates_dir: Optional[Path] = Path("templates/"),
                 template_name: Optional[str] = "package.py.j2",
                 output: Optional[Path] = Path("package.py")):
        """
        Parameters
        ----------
        matches: Dict
            Dictionary contatining the package name and the version constraint.
        metadata: Dict
            Dictionary containing the projects metadata, e.g. name, license, etc.
        templates_dir: str
            Directory containing the jinja2 templates.
        template_name: str
            Jinja2 template name to be rendered.
        """

        logger.info(f"initializing renderer with template: {template_name}")
        self.matches: Dict = matches
        self.parsed_matches: Dict = self._parse_matches()
        self.metadata: Dict = metadata
        self.templates_dir: Path = templates_dir
        self.template_name: str = template_name
        self.template_vars: Dict = {}
        self.template: jinja2.Template = jinja2.Template("")
        self.rendered_content: str = ""
        self.output: Path = output

    def render(self):
        """Renders a template."""

        logger.debug("rendering template")
        loader = jinja2.FileSystemLoader(self.templates_dir)
        env = jinja2.Environment(loader=loader)
        logger.debug("set templates loader and environment")
        self.template = env.get_template(self.template_name)
        vars = self._populate_template_vars()

        self.rendered_content = self.template.render(matches=vars["matches"], metadata=vars["metadata"])
        try:
            with open(self.output, 'w') as f:
                f.write(self.rendered_content)
            logger.debug(f"wrote rendered content to: {self.output}")
        except Exception as e:
            logger.exception(f"exception {e} occured when writing to: {self.output}")

    def _populate_template_vars(self) -> Dict:
        """Populate template variables.

        Returns
        -------
        Dict:
            Populated template variables.
        """

        logger.debug("populating template variables")
        vars = {
            "matches":     self.parsed_matches,
            "metadata": {
                    "class_name":  self.metadata["class_name"],
                    "description": self.metadata["description"],
                    "homepage":    self.metadata["homepage"],
                    "url":         self.metadata["url"],
                    "git":         self.metadata["git"],
                    "license":     self.metadata["license"],
                    "version":     self.metadata["version"]
                }
        }
        self.template_vars = vars
        return vars

    def _parse_matches(self) -> Dict:
        """Parse given matches, mainly convert different version types to str.

        Raises
        ------
        RuntimeError:
            When the type of given version could not be determined.

        Returns
        -------
        Dict:
            Parsed given matches.
        """

        logger.debug("parsing given matched versions")
        _matches = self.matches
        dep_types = _matches.keys()
        for dep_type in dep_types:
            logger.debug(f"parsing matched version for dependency type: {dep_type}")
            match_types = _matches[dep_type].keys()
            for match_type in match_types:
                pkgs = _matches[dep_type][match_type]
                for pkg in pkgs:
                    if isinstance(pkg["version"], Version):
                        pkg["version"] = self._version_to_str(pkg["version"])
                    elif isinstance(pkg["version"], SpecifierSet):
                        pkg["version"] = self._specifierset_to_str(pkg["version"])
                    else:
                        raise RuntimeError(f"could not handle version type, {pkg['name']}: {pkg['version']}")
        return _matches

    def _version_to_str(self, version: Version) -> str:
        """Convert a Version type to str.

        Parameters
        ----------
        version: Version
            Given version of type Version to convert.

        Returns
        -------
        str:
            String casted version.
        """

        logger.debug(f"string casting for Version: {version}")
        return str(version)

    def _specifierset_to_str(self, specifierset: SpecifierSet) -> str:
        """Convert an SpecifierSet type to str.

        Parameters
        ----------
        specifiers: SpecifierSet
            Given version of type SpecifierSet to convert.

        Returns
        -------
        str:
            String casted version.
        """

        logger.debug(f"string casting for SpecifierSet: {specifierset}")
        replacements = {">=": '', "<=": '', "==": '', '>': '', '<': '', '=': ''}
        replacements = dict((re.escape(k), v) for k, v in replacements.items())
        pattern = re.compile('|'.join(replacements.keys()))
        raw_specifierset_str = str(specifierset)
        parsed_specifier_set_str = pattern.sub(lambda m: replacements[re.escape(m.group(0))], raw_specifierset_str)
        return parsed_specifier_set_str
