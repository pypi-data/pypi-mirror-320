import glob
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import click
import requests

from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import echo_safe_humanfriendly_tables_format_smart_table
from tinybird.tb.modules.feedback_manager import FeedbackManager


def project_files(project_path: Path) -> List[str]:
    project_file_extensions = ("datasource", "pipe")
    project_files = []
    for extension in project_file_extensions:
        for project_file in glob.glob(f"{project_path}/**/*.{extension}", recursive=True):
            logging.debug(f"Found project file: {project_file}")
            project_files.append(project_file)
    return project_files


def promote_deployment(host: Optional[str], headers: dict) -> None:
    TINYBIRD_API_URL = f"{host}/v1/deployments"
    r = requests.get(TINYBIRD_API_URL, headers=headers)
    result = r.json()
    logging.debug(json.dumps(result, indent=2))

    deployments = result.get("deployments")
    if not deployments:
        click.echo(FeedbackManager.error(message="No deployments found"))
        return

    if len(deployments) < 2:
        click.echo(FeedbackManager.error(message="Only one deployment found"))
        return

    last_deployment, candidate_deployment = deployments[0], deployments[1]

    if candidate_deployment.get("status") != "data_ready":
        click.echo(FeedbackManager.error(message="Current deployment is not ready"))
        return

    if candidate_deployment.get("live"):
        click.echo(FeedbackManager.error(message="Candidate deployment is already live"))
    else:
        click.echo(FeedbackManager.success(message="Promoting deployment"))

        TINYBIRD_API_URL = f"{host}/v1/deployments/{candidate_deployment.get('id')}/set-live"
        r = requests.post(TINYBIRD_API_URL, headers=headers)
        result = r.json()
        logging.debug(json.dumps(result, indent=2))

    click.echo(FeedbackManager.success(message="Removing old deployment"))

    TINYBIRD_API_URL = f"{host}/v1/deployments/{last_deployment.get('id')}"
    r = requests.delete(TINYBIRD_API_URL, headers=headers)
    result = r.json()
    logging.debug(json.dumps(result, indent=2))

    click.echo(FeedbackManager.success(message="Deployment promoted successfully"))


def rollback_deployment(host: Optional[str], headers: dict) -> None:
    TINYBIRD_API_URL = f"{host}/v1/deployments"
    r = requests.get(TINYBIRD_API_URL, headers=headers)
    result = r.json()
    logging.debug(json.dumps(result, indent=2))

    deployments = result.get("deployments")
    if not deployments:
        click.echo(FeedbackManager.error(message="No deployments found"))
        return

    if len(deployments) < 2:
        click.echo(FeedbackManager.error(message="Only one deployment found"))
        return

    previous_deployment, current_deployment = deployments[0], deployments[1]

    if previous_deployment.get("status") != "data_ready":
        click.echo(FeedbackManager.error(message="Previous deployment is not ready"))
        return

    if previous_deployment.get("live"):
        click.echo(FeedbackManager.error(message="Previous deployment is already live"))
    else:
        click.echo(FeedbackManager.success(message="Promoting previous deployment"))

        TINYBIRD_API_URL = f"{host}/v1/deployments/{previous_deployment.get('id')}/set-live"
        r = requests.post(TINYBIRD_API_URL, headers=headers)
        result = r.json()
        logging.debug(json.dumps(result, indent=2))

    click.echo(FeedbackManager.success(message="Removing current deployment"))

    TINYBIRD_API_URL = f"{host}/v1/deployments/{current_deployment.get('id')}"
    r = requests.delete(TINYBIRD_API_URL, headers=headers)
    result = r.json()
    logging.debug(json.dumps(result, indent=2))

    click.echo(FeedbackManager.success(message="Deployment rolled back successfully"))


@cli.group(name="deployment")
def deployment_group() -> None:
    """
    Deployment commands.
    """
    pass


@deployment_group.command(name="create")
@click.argument("project_path", type=click.Path(exists=True), default=Path.cwd())
@click.option(
    "--wait/--no-wait",
    is_flag=True,
    default=False,
    help="Wait for deploy to finish. Disabled by default.",
)
@click.option(
    "--auto/--no-auto",
    is_flag=True,
    default=False,
    help="Auto-promote the deployment. Only works if --wait is enabled. Disabled by default.",
)
@click.pass_context
def create(ctx: click.Context, project_path: Path, wait: bool, auto: bool) -> None:
    """
    Validate and deploy the project server side.
    """
    # TODO: This code is duplicated in build_server.py
    # Should be refactored to be shared
    MULTIPART_BOUNDARY_DATA_PROJECT = "data_project://"
    DATAFILE_TYPE_TO_CONTENT_TYPE = {
        ".datasource": "text/plain",
        ".pipe": "text/plain",
    }

    client = ctx.ensure_object(dict)["client"]
    TINYBIRD_API_URL = f"{client.host}/v1/deploy"
    TINYBIRD_API_KEY = client.token

    files = [
        ("context://", ("cli-version", "1.0.0", "text/plain")),
    ]
    fds = []
    for file_path in project_files(project_path):
        relative_path = str(Path(file_path).relative_to(project_path))
        fd = open(file_path, "rb")
        fds.append(fd)
        content_type = DATAFILE_TYPE_TO_CONTENT_TYPE.get(Path(file_path).suffix, "application/unknown")
        files.append((MULTIPART_BOUNDARY_DATA_PROJECT, (relative_path, fd.read().decode("utf-8"), content_type)))

    deployment = None
    try:
        HEADERS = {"Authorization": f"Bearer {TINYBIRD_API_KEY}"}

        r = requests.post(TINYBIRD_API_URL, files=files, headers=HEADERS)
        result = r.json()
        logging.debug(json.dumps(result, indent=2))

        deploy_result = result.get("result")
        if deploy_result == "success":
            click.echo(FeedbackManager.success(message="Deploy submitted successfully"))
            deployment = result.get("deployment")
        elif deploy_result == "failed":
            click.echo(FeedbackManager.error(message="Deploy failed"))
            deploy_errors = result.get("errors")
            for deploy_error in deploy_errors:
                if deploy_error.get("filename", None):
                    click.echo(
                        FeedbackManager.error(message=f"{deploy_error.get('filename')}\n\n{deploy_error.get('error')}")
                    )
                else:
                    click.echo(FeedbackManager.error(message=f"{deploy_error.get('error')}"))
        else:
            click.echo(FeedbackManager.error(message=f"Unknown build result {deploy_result}"))
    finally:
        for fd in fds:
            fd.close()

    if deployment and wait:
        while deployment.get("status") != "data_ready":
            time.sleep(5)
            TINYBIRD_API_URL = f"{client.host}/v1/deployments/{deployment.get('id')}"
            r = requests.get(TINYBIRD_API_URL, headers=HEADERS)
            result = r.json()
            deployment = result.get("deployment")
            if deployment.get("status") == "failed":
                click.echo(FeedbackManager.error(message="Deployment failed"))
                if auto:
                    click.echo(FeedbackManager.error(message="Rolling back deployment"))
                    rollback_deployment(client.host, HEADERS)
                return

        click.echo(FeedbackManager.success(message="Deployment is ready"))

        if auto:
            promote_deployment(client.host, HEADERS)


@deployment_group.command(name="ls")
@click.argument("project_path", type=click.Path(exists=True), default=Path.cwd())
@click.pass_context
def deployment_ls(ctx: click.Context, project_path: Path) -> None:
    """
    List all the deployments you have in the project.
    """
    client = ctx.ensure_object(dict)["client"]

    TINYBIRD_API_KEY = client.token
    HEADERS = {"Authorization": f"Bearer {TINYBIRD_API_KEY}"}
    TINYBIRD_API_URL = f"{client.host}/v1/deployments"

    r = requests.get(TINYBIRD_API_URL, headers=HEADERS)
    result = r.json()
    logging.debug(json.dumps(result, indent=2))

    status_map = {"data_ready": "Ready", "failed": "Failed"}
    columns = ["ID", "Status", "Created at", "Live"]
    table = []
    for deployment in result.get("deployments"):
        table.append(
            [
                deployment.get("id"),
                status_map.get(deployment.get("status"), "In progress"),
                datetime.fromisoformat(deployment.get("created_at")).strftime("%Y-%m-%d %H:%M:%S"),
                deployment.get("live"),
            ]
        )

    echo_safe_humanfriendly_tables_format_smart_table(table, column_names=columns)


@deployment_group.command(name="promote")
@click.argument("project_path", type=click.Path(exists=True), default=Path.cwd())
@click.pass_context
def deployment_promote(ctx: click.Context, project_path: Path) -> None:
    """
    Promote last deploy to ready and remove old one.
    """
    client = ctx.ensure_object(dict)["client"]

    TINYBIRD_API_KEY = client.token
    HEADERS = {"Authorization": f"Bearer {TINYBIRD_API_KEY}"}

    promote_deployment(client.host, HEADERS)


@deployment_group.command(name="rollback")
@click.argument("project_path", type=click.Path(exists=True), default=Path.cwd())
@click.pass_context
def deployment_rollback(ctx: click.Context, project_path: Path) -> None:
    """
    Rollback to the previous deployment.
    """
    client = ctx.ensure_object(dict)["client"]

    TINYBIRD_API_KEY = client.token
    HEADERS = {"Authorization": f"Bearer {TINYBIRD_API_KEY}"}

    rollback_deployment(client.host, HEADERS)
