import os

import click
import river_print as rp

from .path_manager import generate_path_manager


@click.command()
@click.argument("project_root_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-v", "--verbose", is_flag=True, help="verbose mode")
def main(
    project_root_dir,
    verbose,
):
    if project_root_dir is None:
        project_root_dir = os.getcwd()
    generate_path_manager(project_root_dir)


if __name__ == "main":
    main()
