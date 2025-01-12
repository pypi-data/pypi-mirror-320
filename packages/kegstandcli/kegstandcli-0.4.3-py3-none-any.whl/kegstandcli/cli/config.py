"""Configuration handling for Kegstand CLI."""

import re
from pathlib import Path
from typing import Any

import click
from tomlkit import loads as parse_toml

CONFIG_FILE_NAMES = ["kegstand.toml", ".kegstand", "pyproject.toml"]


def find_config_file(verbose: bool, config_file: str | None) -> str | None:  # noqa: ARG001
    """Find the configuration file to use.

    Args:
        verbose: Whether to show verbose output
        config_file: Path to the configuration file, or None to search for one

    Returns:
        str | None: Path to the configuration file, or None if not found
    """
    # If no config file is specified, locate it automatically
    if config_file is None:
        for name in CONFIG_FILE_NAMES:
            if Path(name).exists():
                config_file = name
                break

    if not config_file or not Path(config_file).exists():
        if verbose:
            click.echo(f"Configuration file not found: {config_file}")
        return None

    return config_file


def get_kegstand_config(verbose: bool, project_dir: str, config_file: str) -> dict[str, Any]:  # noqa: PLR0912
    """Load and parse the Kegstand configuration.

    Args:
        verbose: Whether to show verbose output
        project_dir: Path to the project directory
        config_file: Path to the configuration file

    Returns:
        dict: The parsed configuration

    Raises:
        click.BadParameter: If the project name is invalid
        FileNotFoundError: If the configuration file is not found
    """
    config_path = Path(project_dir) / config_file
    if verbose:
        click.echo(f"Loading configuration from {config_path}")

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    parsed_toml_config = parse_toml(config_path.read_text(encoding="utf-8"))

    # If the config file is pyproject.toml, the config will be under the 'tool.kegstand' key
    if config_file.endswith("pyproject.toml"):
        config = parsed_toml_config.get("tool", {}).get("kegstand", {})
        # Some keys are used from the [project] or [tool.poetry] section
        # if not specified in [tool.kegstand]
        properties_from_pyproject = ["name", "description", "version"]
        if "project" not in config:
            config["project"] = {}
        for property_name in properties_from_pyproject:
            if property_name not in config["project"]:
                # Try to get the property from the [project] section
                if property_name in parsed_toml_config.get("project", {}):
                    config["project"][property_name] = parsed_toml_config.get("project", {}).get(
                        property_name
                    )
                # Try to get the property from the [tool.poetry] section
                elif property_name in parsed_toml_config.get("tool", {}).get("poetry", {}):
                    config["project"][property_name] = (
                        parsed_toml_config.get("tool", {}).get("poetry", {}).get(property_name)
                    )
    else:
        config = parsed_toml_config

    # Validate that the name follows PEP 508
    name_regex = r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$"
    if not re.match(name_regex, config["project"]["name"], flags=re.IGNORECASE):
        raise click.BadParameter(
            f"Name '{config['project']['name']}' is not following PEP 508 naming conventions."
        )

    config["project_dir"] = str(config_path.parent)
    config["config_file"] = str(config_path)

    # Set defaults where missing
    config_defaults = {
        "api": {"name": "Untitled API", "entrypoint": "api.lambda.handler", "runtime": "python3.13"}
    }
    for section, defaults in config_defaults.items():
        if section not in config:
            config[section] = {}
        for key, default in defaults.items():
            if key not in config[section]:
                config[section][key] = default

    return config
