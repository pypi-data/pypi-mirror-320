import rich_click as click

from union._config import _DEFAULT_DOMAIN, _DEFAULT_PROJECT
from union.remote._app_remote import AppRemote


@click.group()
def stop():
    """Stop a resource."""


@stop.command()
@click.argument("name", type=str)
@click.option("--project", default=_DEFAULT_PROJECT, help="Project name")
@click.option("--domain", default=_DEFAULT_DOMAIN, help="Domain name")
def apps(name: str, project: str, domain: str):
    app_remote = AppRemote(project=project, domain=domain)
    app_remote.stop(name=name)
