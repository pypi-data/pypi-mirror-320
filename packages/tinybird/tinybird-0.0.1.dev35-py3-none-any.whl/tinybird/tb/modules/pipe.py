# This is a command file for our CLI. Please keep it clean.
#
# - If it makes sense and only when strictly necessary, you can create utility functions in this file.
# - But please, **do not** interleave utility functions and command definitions.

import json
import re
from typing import Dict, List, Optional, Tuple

import click
import humanfriendly
from click import Context

from tinybird.client import AuthNoTokenException, DoesNotExistException, TinyB
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import (
    coro,
    create_tb_client,
    echo_safe_humanfriendly_tables_format_smart_table,
    wait_job,
)
from tinybird.tb.modules.datafile.common import PipeTypes, get_name_version
from tinybird.tb.modules.exceptions import CLIPipeException
from tinybird.tb.modules.feedback_manager import FeedbackManager


@cli.group(hidden=True)
@click.pass_context
def pipe(ctx):
    """Pipes commands"""


@pipe.group(name="copy")
@click.pass_context
def pipe_copy(ctx: Context) -> None:
    """Copy Pipe commands"""


@pipe.group(name="sink")
@click.pass_context
def pipe_sink(ctx: Context) -> None:
    """Sink Pipe commands"""


@pipe.command(name="stats")
@click.argument("pipes", nargs=-1)
@click.option(
    "--format",
    "format_",
    type=click.Choice(["json"], case_sensitive=False),
    default=None,
    help="Force a type of the output. To parse the output, keep in mind to use `tb --no-version-warning pipe stats`  option.",
)
@click.pass_context
@coro
async def pipe_stats(ctx: click.Context, pipes: Tuple[str, ...], format_: str):
    """
    Print pipe stats for the last 7 days
    """
    client: TinyB = ctx.ensure_object(dict)["client"]
    all_pipes = await client.pipes()
    pipes_to_get_stats = []
    pipes_ids: Dict = {}

    if pipes:
        # We filter by the pipes we want to look for
        all_pipes = [pipe for pipe in all_pipes if pipe["name"] in pipes]

    for pipe in all_pipes:
        name_version = get_name_version(pipe["name"])
        if name_version["name"] in pipe["name"]:
            pipes_to_get_stats.append(f"'{pipe['id']}'")
            pipes_ids[pipe["id"]] = name_version

    if not pipes_to_get_stats:
        if format_ == "json":
            click.echo(json.dumps({"pipes": []}, indent=2))
        else:
            click.echo(FeedbackManager.info_no_pipes_stats())
        return

    sql = f"""
        SELECT
            pipe_id id,
            sumIf(view_count, date > now() - interval 7 day) requests,
            sumIf(error_count, date > now() - interval 7 day) errors,
            avgMergeIf(avg_duration_state, date > now() - interval 7 day) latency
        FROM tinybird.pipe_stats
        WHERE pipe_id in ({','.join(pipes_to_get_stats)})
        GROUP BY pipe_id
        ORDER BY requests DESC
        FORMAT JSON
    """

    res = await client.query(sql)

    if res and "error" in res:
        raise CLIPipeException(FeedbackManager.error_exception(error=str(res["error"])))

    columns = ["version", "name", "request count", "error count", "avg latency"]
    table_human_readable: List[Tuple] = []
    table_machine_readable: List[Dict] = []
    if res and "data" in res:
        for x in res["data"]:
            tk = pipes_ids[x["id"]]
            table_human_readable.append(
                (
                    tk["version"] if tk["version"] is not None else "",
                    tk["name"],
                    x["requests"],
                    x["errors"],
                    x["latency"],
                )
            )
            table_machine_readable.append(
                {
                    "version": tk["version"] if tk["version"] is not None else "",
                    "name": tk["name"],
                    "requests": x["requests"],
                    "errors": x["errors"],
                    "latency": x["latency"],
                }
            )

        table_human_readable.sort(key=lambda x: (x[1], x[0]))
        table_machine_readable.sort(key=lambda x: x["name"])

        if format_ == "json":
            click.echo(json.dumps({"pipes": table_machine_readable}, indent=2))
        else:
            echo_safe_humanfriendly_tables_format_smart_table(table_human_readable, column_names=columns)


@pipe.command(name="ls")
@click.option("--match", default=None, help="Retrieve any resourcing matching the pattern. eg --match _test")
@click.option(
    "--format",
    "format_",
    type=click.Choice(["json"], case_sensitive=False),
    default=None,
    help="Force a type of the output",
)
@click.pass_context
@coro
async def pipe_ls(ctx: Context, match: str, format_: str):
    """List pipes"""

    client: TinyB = ctx.ensure_object(dict)["client"]
    pipes = await client.pipes(dependencies=False, node_attrs="name", attrs="name,updated_at")
    pipes = sorted(pipes, key=lambda p: p["updated_at"])

    columns = ["version", "name", "published date", "nodes"]
    table_human_readable = []
    table_machine_readable = []
    pattern = re.compile(match) if match else None
    for t in pipes:
        tk = get_name_version(t["name"])
        if pattern and not pattern.search(tk["name"]):
            continue
        table_human_readable.append(
            (tk["version"] if tk["version"] is not None else "", tk["name"], t["updated_at"][:-7], len(t["nodes"]))
        )
        table_machine_readable.append(
            {
                "version": tk["version"] if tk["version"] is not None else "",
                "name": tk["name"],
                "published date": t["updated_at"][:-7],
                "nodes": len(t["nodes"]),
            }
        )

    if not format_:
        click.echo(FeedbackManager.info_pipes())
        echo_safe_humanfriendly_tables_format_smart_table(table_human_readable, column_names=columns)
        click.echo("\n")
    elif format_ == "json":
        click.echo(json.dumps({"pipes": table_machine_readable}, indent=2))
    else:
        raise CLIPipeException(FeedbackManager.error_pipe_ls_type())


@pipe.command(name="populate")
@click.argument("pipe_name")
@click.option("--node", type=str, help="Name of the materialized node.", default=None, required=False)
@click.option(
    "--sql-condition",
    type=str,
    default=None,
    help="Populate with a SQL condition to be applied to the trigger Data Source of the Materialized View. For instance, `--sql-condition='date == toYYYYMM(now())'` it'll populate taking all the rows from the trigger Data Source which `date` is the current month. Use it together with --populate. --sql-condition is not taken into account if the --subset param is present. Including in the ``sql_condition`` any column present in the Data Source ``engine_sorting_key`` will make the populate job process less data.",
)
@click.option(
    "--truncate", is_flag=True, default=False, help="Truncates the materialized Data Source before populating it."
)
@click.option(
    "--unlink-on-populate-error",
    is_flag=True,
    default=False,
    help="If the populate job fails the Materialized View is unlinked and new data won't be ingested in the Materialized View. First time a populate job fails, the Materialized View is always unlinked.",
)
@click.option(
    "--wait",
    is_flag=True,
    default=False,
    help="Waits for populate jobs to finish, showing a progress bar. Disabled by default.",
)
@click.pass_context
@coro
async def pipe_populate(
    ctx: click.Context,
    pipe_name: str,
    node: str,
    sql_condition: str,
    truncate: bool,
    unlink_on_populate_error: bool,
    wait: bool,
):
    """Populate the result of a Materialized Node into the target Materialized View"""
    cl = create_tb_client(ctx)

    pipe = await cl.pipe(pipe_name)

    if pipe["type"] != PipeTypes.MATERIALIZED:
        raise CLIPipeException(FeedbackManager.error_pipe_not_materialized(pipe=pipe_name))

    if not node:
        materialized_ids = [pipe_node["id"] for pipe_node in pipe["nodes"] if pipe_node.get("materialized") is not None]

        if not materialized_ids:
            raise CLIPipeException(FeedbackManager.error_populate_no_materialized_in_pipe(pipe=pipe_name))

        elif len(materialized_ids) > 1:
            raise CLIPipeException(FeedbackManager.error_populate_several_materialized_in_pipe(pipe=pipe_name))

        node = materialized_ids[0]

    response = await cl.populate_node(
        pipe_name,
        node,
        populate_condition=sql_condition,
        truncate=truncate,
        unlink_on_populate_error=unlink_on_populate_error,
    )
    if "job" not in response:
        raise CLIPipeException(response)

    job_id = response["job"]["id"]
    job_url = response["job"]["job_url"]
    if sql_condition:
        click.echo(FeedbackManager.info_populate_condition_job_url(url=job_url, populate_condition=sql_condition))
    else:
        click.echo(FeedbackManager.info_populate_job_url(url=job_url))
    if wait:
        await wait_job(cl, job_id, job_url, "Populating")


@pipe.command(name="token_read")
@click.argument("pipe_name")
@click.pass_context
@coro
async def pipe_token_read(ctx: click.Context, pipe_name: str):
    """Retrieve a token to read a pipe"""
    client: TinyB = ctx.ensure_object(dict)["client"]

    try:
        await client.pipe_file(pipe_name)
    except DoesNotExistException:
        raise CLIPipeException(FeedbackManager.error_pipe_does_not_exist(pipe=pipe_name))

    tokens = await client.tokens()
    token = None

    for t in tokens:
        for scope in t["scopes"]:
            if scope["type"] == "PIPES:READ" and scope["resource"] == pipe_name:
                token = t["token"]
    if token:
        click.echo(token)
    else:
        click.echo(FeedbackManager.warning_token_pipe(pipe=pipe_name))


@pipe.command(
    name="data",
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    ),
)
@click.argument("pipe")
@click.option("--query", default=None, help="Run SQL over pipe results")
@click.option(
    "--format", "format_", type=click.Choice(["json", "csv"], case_sensitive=False), help="Return format (CSV, JSON)"
)
@click.pass_context
@coro
async def print_pipe(ctx: Context, pipe: str, query: str, format_: str):
    """Print data returned by a pipe

    Syntax: tb pipe data <pipe_name> --param_name value --param2_name value2 ...
    """

    client: TinyB = ctx.ensure_object(dict)["client"]
    params = {ctx.args[i][2:]: ctx.args[i + 1] for i in range(0, len(ctx.args), 2)}
    req_format = "json" if not format_ else format_.lower()
    try:
        res = await client.pipe_data(pipe, format=req_format, sql=query, params=params)
    except AuthNoTokenException:
        raise
    except Exception as e:
        raise CLIPipeException(FeedbackManager.error_exception(error=str(e)))

    if not format_:
        stats = res["statistics"]
        seconds = stats["elapsed"]
        rows_read = humanfriendly.format_number(stats["rows_read"])
        bytes_read = humanfriendly.format_size(stats["bytes_read"])

        click.echo(FeedbackManager.success_print_pipe(pipe=pipe))
        click.echo(FeedbackManager.info_query_stats(seconds=seconds, rows=rows_read, bytes=bytes_read))

        if not res["data"]:
            click.echo(FeedbackManager.info_no_rows())
        else:
            echo_safe_humanfriendly_tables_format_smart_table(
                data=[d.values() for d in res["data"]], column_names=res["data"][0].keys()
            )
        click.echo("\n")
    elif req_format == "json":
        click.echo(json.dumps(res))
    else:
        click.echo(res)


@pipe_copy.command(name="run", short_help="Run an on-demand copy job")
@click.argument("pipe_name_or_id")
@click.option("--wait", is_flag=True, default=False, help="Wait for the copy job to finish")
@click.option(
    "--mode", type=click.Choice(["append", "replace"], case_sensitive=True), default=None, help="Copy strategy"
)
@click.option("--yes", is_flag=True, default=False, help="Do not ask for confirmation")
@click.option(
    "--param",
    nargs=1,
    type=str,
    multiple=True,
    default=None,
    help="Key and value of the params you want the Copy pipe to be called with. For example: tb pipe copy run <my_copy_pipe> --param foo=bar",
)
@click.pass_context
@coro
async def pipe_copy_run(
    ctx: click.Context, pipe_name_or_id: str, wait: bool, mode: str, yes: bool, param: Optional[Tuple[str]]
):
    """Run an on-demand copy job"""

    params = dict(key_value.split("=") for key_value in param) if param else {}

    if yes or click.confirm(FeedbackManager.warning_confirm_copy_pipe(pipe=pipe_name_or_id)):
        click.echo(FeedbackManager.info_copy_job_running(pipe=pipe_name_or_id))
        client: TinyB = ctx.ensure_object(dict)["client"]

        try:
            response = await client.pipe_run_copy(pipe_name_or_id, params, mode)

            job_id = response["job"]["job_id"]
            job_url = response["job"]["job_url"]
            target_datasource_id = response["tags"]["copy_target_datasource"]
            target_datasource = await client.get_datasource(target_datasource_id)
            target_datasource_name = target_datasource["name"]
            click.echo(
                FeedbackManager.success_copy_job_created(target_datasource=target_datasource_name, job_url=job_url)
            )

            if wait:
                await wait_job(client, job_id, job_url, "** Copying data")
                click.echo(FeedbackManager.success_data_copied_to_ds(target_datasource=target_datasource_name))

        except AuthNoTokenException:
            raise
        except Exception as e:
            raise CLIPipeException(FeedbackManager.error_creating_copy_job(error=e))


@pipe_copy.command(name="resume", short_help="Resume a paused copy pipe")
@click.argument("pipe_name_or_id")
@click.pass_context
@coro
async def pipe_copy_resume(ctx: click.Context, pipe_name_or_id: str):
    """Resume a paused copy pipe"""

    click.echo(FeedbackManager.info_copy_pipe_resuming(pipe=pipe_name_or_id))
    client: TinyB = ctx.ensure_object(dict)["client"]

    try:
        await client.pipe_resume_copy(pipe_name_or_id)
        click.echo(FeedbackManager.success_copy_pipe_resumed(pipe=pipe_name_or_id))

    except AuthNoTokenException:
        raise
    except Exception as e:
        raise CLIPipeException(FeedbackManager.error_resuming_copy_pipe(error=e))


@pipe_copy.command(name="pause", short_help="Pause a running copy pipe")
@click.argument("pipe_name_or_id")
@click.pass_context
@coro
async def pipe_copy_pause(ctx: click.Context, pipe_name_or_id: str):
    """Pause a running copy pipe"""

    click.echo(FeedbackManager.info_copy_pipe_pausing(pipe=pipe_name_or_id))
    client: TinyB = ctx.ensure_object(dict)["client"]

    try:
        await client.pipe_pause_copy(pipe_name_or_id)
        click.echo(FeedbackManager.success_copy_pipe_paused(pipe=pipe_name_or_id))

    except AuthNoTokenException:
        raise
    except Exception as e:
        raise CLIPipeException(FeedbackManager.error_pausing_copy_pipe(error=e))


@pipe_sink.command(name="run", short_help="Run an on-demand sink job")
@click.argument("pipe_name_or_id")
@click.option("--wait", is_flag=True, default=False, help="Wait for the sink job to finish")
@click.option("--yes", is_flag=True, default=False, help="Do not ask for confirmation")
@click.option("--dry-run", is_flag=True, default=False, help="Run the command without executing the sink job")
@click.option(
    "--param",
    nargs=1,
    type=str,
    multiple=True,
    default=None,
    help="Key and value of the params you want the Sink pipe to be called with. For example: tb pipe sink run <my_sink_pipe> --param foo=bar",
)
@click.pass_context
@coro
async def pipe_sink_run(
    ctx: click.Context, pipe_name_or_id: str, wait: bool, yes: bool, dry_run: bool, param: Optional[Tuple[str]]
):
    """Run an on-demand sink job"""

    params = dict(key_value.split("=") for key_value in param) if param else {}

    if dry_run or yes or click.confirm(FeedbackManager.warning_confirm_sink_job(pipe=pipe_name_or_id)):
        click.echo(FeedbackManager.info_sink_job_running(pipe=pipe_name_or_id))
        client: TinyB = ctx.ensure_object(dict)["client"]

        try:
            pipe = await client.pipe(pipe_name_or_id)
            connections = await client.get_connections()

            if (pipe.get("type", None) != "sink") or (not pipe.get("sink_node", None)):
                error_message = f"Pipe {pipe_name_or_id} is not published as a Sink pipe"
                raise Exception(FeedbackManager.error_running_on_demand_sink_job(error=error_message))

            current_sink = None
            for connection in connections:
                for sink in connection.get("sinks", []):
                    if sink.get("resource_id") == pipe["id"]:
                        current_sink = sink
                        break

            if not current_sink:
                click.echo(FeedbackManager.warning_sink_no_connection(pipe_name=pipe.get("name", "")))

            if dry_run:
                click.echo(FeedbackManager.info_dry_sink_run())
                return

            bucket_path = (current_sink or {}).get("settings", {}).get("bucket_path", "")
            response = await client.pipe_run_sink(pipe_name_or_id, params)
            job_id = response["job"]["id"]
            job_url = response["job"]["job_url"]
            click.echo(FeedbackManager.success_sink_job_created(bucket_path=bucket_path, job_url=job_url))

            if wait:
                await wait_job(client, job_id, job_url, "** Sinking data")
                click.echo(FeedbackManager.success_sink_job_finished(bucket_path=bucket_path))

        except AuthNoTokenException:
            raise
        except Exception as e:
            raise CLIPipeException(FeedbackManager.error_creating_sink_job(error=str(e)))
