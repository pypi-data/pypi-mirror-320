import click

from .convert_ui import convert_ui_to_py
from .generator import create_project


@click.group()
def cli():
    pass


@cli.command()
@click.argument('project_name')
def startproject(project_name):
    create_project(project_name)


@cli.command()
@click.argument('filename', required=False)
def convertui(filename):
    convert_ui_to_py(filename)
