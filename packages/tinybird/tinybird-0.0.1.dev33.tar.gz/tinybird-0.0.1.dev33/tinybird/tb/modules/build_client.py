import asyncio
import os
import threading
import time
from pathlib import Path
from typing import List

import click

import tinybird.context as context
from tinybird.client import TinyB
from tinybird.config import FeatureFlags
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import push_data
from tinybird.tb.modules.datafile.build import folder_build
from tinybird.tb.modules.datafile.common import get_project_filenames, get_project_fixtures, has_internal_datafiles
from tinybird.tb.modules.datafile.exceptions import ParseException
from tinybird.tb.modules.datafile.fixture import build_fixture_name, get_fixture_dir
from tinybird.tb.modules.datafile.parse_datasource import parse_datasource
from tinybird.tb.modules.datafile.parse_pipe import parse_pipe
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.local_common import get_tinybird_local_client
from tinybird.tb.modules.shell import Shell, print_table_formatted
from tinybird.tb.modules.watch import watch_files


def is_vendor(f: Path) -> bool:
    return f.parts[0] == "vendor"


def get_vendor_workspace(f: Path) -> str:
    return f.parts[1]


def is_endpoint(f: Path) -> bool:
    return f.suffix == ".pipe" and not is_vendor(f) and f.parts[0] == "endpoints"


def is_pipe(f: Path) -> bool:
    return f.suffix == ".pipe" and not is_vendor(f)


def check_filenames(filenames: List[str]):
    parser_matrix = {".pipe": parse_pipe, ".datasource": parse_datasource}
    incl_suffix = ".incl"

    for filename in filenames:
        if os.path.isdir(filename):
            check_filenames(filenames=get_project_filenames(filename))

        file_suffix = Path(filename).suffix
        if file_suffix == incl_suffix:
            continue

        parser = parser_matrix.get(file_suffix)
        if not parser:
            raise ParseException(FeedbackManager.error_unsupported_datafile(extension=file_suffix))

        parser(filename)


@cli.command()
@click.option(
    "--folder",
    default=".",
    help="Folder from where to execute the command. By default the current folder.",
    hidden=True,
    type=click.types.STRING,
)
@click.option(
    "--watch",
    is_flag=True,
    help="Watch for changes in the files and rebuild them.",
)
def build_client(
    folder: str,
    watch: bool,
) -> None:
    """Build the project in Tinybird Local."""
    ignore_sql_errors = FeatureFlags.ignore_sql_errors()
    context.disable_template_security_validation.set(True)
    is_internal = has_internal_datafiles(folder)
    folder_path = os.path.abspath(folder)
    tb_client = asyncio.run(get_tinybird_local_client(folder_path))

    async def process(filenames: List[str], watch: bool = False):
        datafiles = [f for f in filenames if f.endswith(".datasource") or f.endswith(".pipe")]
        if len(datafiles) > 0:
            check_filenames(filenames=datafiles)
            await folder_build(
                tb_client,
                filenames=datafiles,
                ignore_sql_errors=ignore_sql_errors,
                is_internal=is_internal,
                watch=watch,
                folder=folder,
            )
        if len(filenames) > 0:
            filename = filenames[0]
            if filename.endswith(".ndjson"):
                fixture_path = Path(filename)
                datasources_path = Path(folder) / "datasources"
                ds_name = fixture_path.stem
                ds_path = datasources_path / f"{ds_name}.datasource"

                if not ds_path.exists():
                    try:
                        ds_name = "_".join(fixture_path.stem.split("_")[:-1])
                        ds_path = datasources_path / f"{ds_name}.datasource"
                    except Exception:
                        pass

                if ds_path.exists():
                    await append_datasource(tb_client, ds_name, str(fixture_path))

            if watch:
                if filename.endswith(".datasource"):
                    ds_path = Path(filename)
                    ds_name = ds_path.stem
                    name = build_fixture_name(filename, ds_name, ds_path.read_text())
                    fixture_folder = get_fixture_dir(folder)
                    fixture_path = fixture_folder / f"{name}.ndjson"

                    if not fixture_path.exists():
                        fixture_path = fixture_folder / f"{ds_name}.ndjson"

                    if fixture_path.exists():
                        await append_datasource(tb_client, ds_name, str(fixture_path))

                if not filename.endswith(".ndjson"):
                    await build_and_print_resource(tb_client, filename)

    datafiles = get_project_filenames(folder)
    fixtures = get_project_fixtures(folder)
    filenames = datafiles + fixtures

    async def build_once(filenames: List[str]):
        ok = False
        try:
            click.echo(FeedbackManager.highlight(message="» Building project...\n"))
            time_start = time.time()
            await process(filenames=filenames, watch=False)
            time_end = time.time()
            elapsed_time = time_end - time_start
            for filename in filenames:
                if filename.endswith(".datasource"):
                    ds_path = Path(filename)
                    ds_name = ds_path.stem
                    name = build_fixture_name(filename, ds_name, ds_path.read_text())
                    fixture_folder = get_fixture_dir(folder)
                    fixture_path = fixture_folder / f"{name}.ndjson"

                    if not fixture_path.exists():
                        fixture_path = fixture_folder / f"{ds_name}.ndjson"

                    if fixture_path.exists():
                        await append_datasource(tb_client, ds_name, str(fixture_path))
            click.echo(FeedbackManager.success(message=f"\n✓ Build completed in {elapsed_time:.1f}s"))
            ok = True
        except Exception as e:
            error_path = Path(".tb_error.txt")
            if error_path.exists():
                content = error_path.read_text()
                content += f"\n\n{str(e)}"
                error_path.write_text(content)
            else:
                error_path.write_text(str(e))
            click.echo(FeedbackManager.error_exception(error=e))
            ok = False
        return ok

    build_ok = asyncio.run(build_once(filenames))

    if watch:
        shell = Shell(folder=folder, client=tb_client)
        click.echo(FeedbackManager.gray(message="\nWatching for changes..."))
        watcher_thread = threading.Thread(
            target=watch_files, args=(filenames, process, shell, folder, build_ok), daemon=True
        )
        watcher_thread.start()
        shell.run()


async def build_and_print_resource(tb_client: TinyB, filename: str):
    resource_path = Path(filename)
    name = resource_path.stem
    pipeline = name if filename.endswith(".pipe") else None
    res = await tb_client.query(f"SELECT * FROM {name} FORMAT JSON", pipeline=pipeline)
    print_table_formatted(res, name)


async def append_datasource(
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
