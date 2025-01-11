import asyncio
import glob
import json
import logging
import threading
from pathlib import Path
from typing import List

import click
import requests

from tinybird.client import TinyB
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import push_data
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.local_common import get_tinybird_local_client
from tinybird.tb.modules.shell import Shell
from tinybird.tb.modules.watch import watch_project


@cli.command()
@click.option("--folder", type=str, default=".")
@click.option("--watch", is_flag=True, default=False, help="Watch for changes and rebuild automatically")
def build(folder: str, watch: bool) -> None:
    """
    Validate and build the project server side.
    """

    tb_client = asyncio.run(get_tinybird_local_client(folder))

    def process() -> None:
        build_project(folder, tb_client)

    process()

    if watch:
        shell = Shell(folder=folder, client=tb_client)
        click.echo(FeedbackManager.gray(message="\nWatching for changes..."))
        watcher_thread = threading.Thread(
            target=watch_project,
            args=(shell, process, folder),
            daemon=True,
        )
        watcher_thread.start()
        shell.run()


def get_project_files(project_path: Path) -> List[str]:
    project_file_extensions = ("datasource", "pipe")
    project_files = []
    for extension in project_file_extensions:
        for project_file in glob.glob(f"{project_path}/**/*.{extension}", recursive=True):
            logging.debug(f"Found project file: {project_file}")
            project_files.append(project_file)
    return project_files


def build_project(folder: str, tb_client: TinyB) -> None:
    MULTIPART_BOUNDARY_DATA_PROJECT = "data_project://"
    DATAFILE_TYPE_TO_CONTENT_TYPE = {
        ".datasource": "text/plain",
        ".pipe": "text/plain",
    }
    TINYBIRD_API_URL = tb_client.host + "/v1/build"
    logging.debug(TINYBIRD_API_URL)
    TINYBIRD_API_KEY = tb_client.token
    try:
        files = [
            ("context://", ("cli-version", "1.0.0", "text/plain")),
        ]
        fds = []
        project_path = Path(folder)
        project_files = get_project_files(project_path)
        for file_path in project_files:
            relative_path = str(Path(file_path).relative_to(project_path))
            fd = open(file_path, "rb")
            fds.append(fd)
            content_type = DATAFILE_TYPE_TO_CONTENT_TYPE.get(Path(file_path).suffix, "application/unknown")
            files.append((MULTIPART_BOUNDARY_DATA_PROJECT, (relative_path, fd.read().decode("utf-8"), content_type)))
        HEADERS = {"Authorization": f"Bearer {TINYBIRD_API_KEY}"}

        r = requests.post(TINYBIRD_API_URL, files=files, headers=HEADERS)
        try:
            result = r.json()
        except Exception as e:
            logging.debug(e, exc_info=True)
            click.echo(FeedbackManager.error(message="Couldn't parse response from server"))
            return

        logging.debug(json.dumps(result, indent=2))

        build_result = result.get("result")
        if build_result == "success":
            click.echo(FeedbackManager.success(message="Build completed successfully"))
        elif build_result == "failed":
            click.echo(FeedbackManager.error(message="Build failed"))
            build_errors = result.get("errors")
            for build_error in build_errors:
                filename_bit = f"{build_error.get('filename', '')}"
                error_msg = ((filename_bit + "\n\n") if filename_bit else "") + build_error.get("error")
                click.echo(FeedbackManager.error(message=error_msg))
        else:
            click.echo(FeedbackManager.error(message=f"Unknown build result. Error: {result.get('error')}"))
    except Exception as e:
        click.echo(FeedbackManager.error_exception(error="Error building project: " + str(e)))
    finally:
        for fd in fds:
            fd.close()


async def append_fixture(
    tb_client: TinyB,
    datasource_name: str,
    url: str,
):
    await tb_client.datasource_truncate(datasource_name)
    await push_data(
        tb_client,
        datasource_name,
        url,
        mode="append",
        concurrency=1,
        silent=True,
    )
