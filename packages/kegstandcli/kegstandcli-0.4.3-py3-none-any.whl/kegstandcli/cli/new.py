"""Project creation command for Kegstand CLI."""

import shutil
from io import BytesIO
from pathlib import Path

import click
from copier import run_copy
from directory_tree import DisplayTree  # type: ignore
from yaml import safe_load


@click.command()
@click.pass_context
@click.argument("project_dir", type=click.Path(exists=False))
@click.option("--data-file", type=click.File("r"), help="Path to a Copier input (JSON/YAML) file")
def new(ctx: click.Context, project_dir: str, data_file: BytesIO) -> None:
    """Create a new Kegstand project.

    Args:
        ctx: Click context
        project_dir: Path to create the new project in
        data_file: Path to a Copier input data file
    """
    verbose = ctx.obj["verbose"]
    copier_data: dict = safe_load(data_file.read()) if data_file else {}
    new_command(verbose, project_dir, copier_data)


def new_command(
    verbose: bool, project_dir: str, copier_data: dict | None = None, defaults: bool = False
) -> None:
    """Execute the project creation process.

    Args:
        verbose: Whether to show verbose output
        project_dir: Path to create the new project in
        data_file: Path to a Copier input data file
        defaults: Whether to use default values for Copier input data

    Raises:
        click.ClickException: If the project directory already exists
        click.Abort: If there is an error creating the project
    """
    if not copier_data:
        copier_data = {}
    project_path = Path(project_dir)
    project_name = copier_data.get("project_name", project_path.name)
    project_parent_dir = str(project_path.parent)

    if project_path.exists():
        raise click.ClickException(f"Folder {project_name} already exists")

    try:
        # Copy all the files from the template folder to the project folder
        template_path = "gh:JensRoland/kegstand-project-template.git"
        input_data = {"project_name": project_name, **copier_data}
        run_copy(
            src_path=template_path,
            dst_path=project_parent_dir,
            data=input_data,
            defaults=defaults,
            quiet=not verbose,
        )
        click.echo(f"\n🥂💃🕺 Successfully created {project_name}! 🥂💃🕺\n")
        DisplayTree(project_path, maxDepth=4, ignoreList=["__init__.py"])

    except Exception as err:
        click.echo(f"Error creating project: {err}", err=True)
        if project_path.exists():
            shutil.rmtree(project_path)
        raise click.Abort() from err
