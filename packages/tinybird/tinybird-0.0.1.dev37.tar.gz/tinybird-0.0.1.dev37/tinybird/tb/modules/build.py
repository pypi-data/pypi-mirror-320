import asyncio
import json
import logging
import threading
import time
from pathlib import Path
from typing import Optional

import click
import requests

from tinybird.client import TinyB
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import push_data
from tinybird.tb.modules.datafile.fixture import build_fixture_name, get_fixture_dir
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.local_common import get_tinybird_local_client
from tinybird.tb.modules.project import Project
from tinybird.tb.modules.shell import Shell
from tinybird.tb.modules.watch import watch_project


@cli.command()
@click.option("--watch", is_flag=True, default=False, help="Watch for changes and rebuild automatically")
@click.pass_context
def build(ctx: click.Context, watch: bool) -> None:
    """
    Validate and build the project server side.
    """

    project: Project = ctx.ensure_object(dict)["project"]
    tb_client = asyncio.run(get_tinybird_local_client(str(project.path)))
    click.echo(FeedbackManager.highlight(message="\n» Building project..."))

    time_start = time.time()

    def process(file_changed: Optional[str] = None) -> None:
        if file_changed and file_changed.endswith(".ndjson"):
            rebuild_fixture(project, tb_client, file_changed)
        else:
            build_project(project, tb_client)

    process()

    time_end = time.time()
    elapsed_time = time_end - time_start
    click.echo(FeedbackManager.success(message=f"\n✓ Build completed in {elapsed_time:.1f}s"))

    if watch:
        shell = Shell(project=project, client=tb_client)
        click.echo(FeedbackManager.gray(message="\nWatching for changes..."))
        watcher_thread = threading.Thread(
            target=watch_project,
            args=(shell, process, project),
            daemon=True,
        )
        watcher_thread.start()
        shell.run()


def build_project(project: Project, tb_client: TinyB) -> None:
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
        project_path = project.path
        project_files = project.get_project_files()

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
            datasources = result.get("datasources", [])
            pipes = result.get("pipes", [])
            for ds in datasources:
                ds_path = next((p for p in project_files if p.endswith(ds.get("name") + ".datasource")), None)
                if ds_path:
                    ds_path = ds_path.replace(f"{project.folder}/", "")
                    click.echo(FeedbackManager.info(message=f"✓ {ds_path} created"))
            for pipe in pipes:
                pipe_name = pipe.get("name")
                pipe_path = next((p for p in project_files if p.endswith(pipe_name + ".pipe")), None)
                if pipe_path:
                    pipe_path = pipe_path.replace(f"{project.folder}/", "")
                    click.echo(FeedbackManager.info(message=f"✓ {pipe_path} created"))

            for filename in project_files:
                if filename.endswith(".datasource"):
                    ds_path = Path(filename)
                    ds_name = ds_path.stem
                    name = build_fixture_name(filename, ds_name, ds_path.read_text())
                    fixture_folder = get_fixture_dir(project.folder)
                    fixture_path = fixture_folder / f"{name}.ndjson"

                    if not fixture_path.exists():
                        fixture_path = fixture_folder / f"{ds_name}.ndjson"

                    if fixture_path.exists():
                        append_fixture(tb_client, ds_name, str(fixture_path))

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
        click.echo(FeedbackManager.error_exception(error="Error: " + str(e)))
    finally:
        for fd in fds:
            fd.close()


def append_fixture(
    tb_client: TinyB,
    datasource_name: str,
    url: str,
):
    asyncio.run(tb_client.datasource_truncate(datasource_name))
    asyncio.run(
        push_data(
            tb_client,
            datasource_name,
            url,
            mode="append",
            concurrency=1,
            silent=True,
        )
    )


def rebuild_fixture(project: Project, tb_client: TinyB, fixture_path: str) -> None:
    fixture_path = Path(fixture_path)
    datasources_path = Path(project.folder) / "datasources"
    ds_name = fixture_path.stem

    if ds_name not in project.datasources:
        try:
            ds_name = "_".join(fixture_path.stem.split("_")[:-1])
        except Exception:
            pass

    ds_path = datasources_path / f"{ds_name}.datasource"

    if ds_path.exists():
        append_fixture(tb_client, ds_name, str(fixture_path))
