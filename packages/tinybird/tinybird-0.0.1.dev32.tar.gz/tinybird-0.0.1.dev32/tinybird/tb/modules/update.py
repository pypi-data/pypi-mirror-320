import os
import re
from os import getcwd
from pathlib import Path
from typing import Optional

import click

from tinybird.client import TinyB
from tinybird.prompts import mock_prompt, update_prompt
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import check_user_token_with_client, coro, generate_datafile
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.datafile.fixture import build_fixture_name, persist_fixture
from tinybird.tb.modules.exceptions import CLIException
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.llm import LLM
from tinybird.tb.modules.llm_utils import extract_xml, parse_xml
from tinybird.tb.modules.local_common import get_tinybird_local_client


@cli.command()
@click.argument("prompt")
@click.option(
    "--folder",
    default=".",
    type=click.Path(exists=False, file_okay=False),
    help="Folder where project files will be placed",
)
@coro
async def update(
    prompt: str,
    folder: str,
) -> None:
    """Update resources in the project."""
    folder = folder or getcwd()
    folder_path = Path(folder)
    if not folder_path.exists():
        folder_path.mkdir()

    try:
        config = CLIConfig.get_project_config(folder)
        tb_client = config.get_client()
        user_token: Optional[str] = None
        try:
            user_token = config.get_user_token()
            if not user_token:
                raise CLIException("No user token found")
            await check_user_token_with_client(tb_client, token=user_token)
        except Exception as e:
            click.echo(
                FeedbackManager.error(message=f"This action requires authentication. Run 'tb login' first. Error: {e}")
            )
            return

        local_client = await get_tinybird_local_client(folder)

        click.echo(FeedbackManager.highlight(message="\n» Updating resources..."))
        datasources_updated = await update_resources(tb_client, user_token, prompt, folder)
        click.echo(FeedbackManager.success(message="✓ Done!\n"))

        if datasources_updated and user_token:
            click.echo(FeedbackManager.highlight(message="\n» Generating fixtures..."))

            datasource_files = [f for f in os.listdir(Path(folder) / "datasources") if f.endswith(".datasource")]
            for datasource_file in datasource_files:
                datasource_path = Path(folder) / "datasources" / datasource_file
                llm = LLM(user_token=user_token, client=tb_client)
                datasource_name = datasource_path.stem
                datasource_content = datasource_path.read_text()
                has_json_path = "`json:" in datasource_content
                if has_json_path:
                    prompt = f"<datasource_schema>{datasource_content}</datasource_schema>\n<user_input>{prompt}</user_input>"
                    response = await llm.ask(system_prompt=mock_prompt(rows=20), prompt=prompt)
                    sql = extract_xml(response, "sql")
                    sql = sql.split("FORMAT")[0]
                    result = await local_client.query(f"{sql} FORMAT JSON")
                    data = result.get("data", [])
                    fixture_name = build_fixture_name(
                        datasource_path.absolute().as_posix(), datasource_name, datasource_content
                    )
                    if data:
                        persist_fixture(fixture_name, data, folder)
                        click.echo(FeedbackManager.info(message=f"✓ /fixtures/{datasource_name}"))

            click.echo(FeedbackManager.success(message="✓ Done!\n"))
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"Error: {str(e)}"))


async def update_resources(
    tb_client: TinyB,
    user_token: str,
    prompt: str,
    folder: str,
):
    datasource_paths = [
        Path(folder) / "datasources" / f for f in os.listdir(Path(folder) / "datasources") if f.endswith(".datasource")
    ]
    pipes_paths = [
        Path(folder) / "endpoints" / f for f in os.listdir(Path(folder) / "endpoints") if f.endswith(".pipe")
    ]
    resources_xml = "\n".join(
        [
            f"<resource><type>{resource_type}</type><name>{resource_name}</name><content>{resource_content}</content></resource>"
            for resource_type, resource_name, resource_content in [
                ("datasource", ds.stem, ds.read_text()) for ds in datasource_paths
            ]
            + [
                (
                    "pipe",
                    pipe.stem,
                    pipe.read_text(),
                )
                for pipe in pipes_paths
            ]
        ]
    )
    llm = LLM(user_token=user_token, client=tb_client)
    result = await llm.ask(system_prompt=update_prompt(resources_xml), prompt=prompt)
    result = extract_xml(result, "response")
    resources = parse_xml(result, "resource")
    datasources = []
    pipes = []
    for resource_xml in resources:
        resource_type = extract_xml(resource_xml, "type")
        name = extract_xml(resource_xml, "name")
        content = extract_xml(resource_xml, "content")
        resource = {
            "name": name,
            "content": content,
        }
        if resource_type.lower() == "datasource":
            datasources.append(resource)
        elif resource_type.lower() == "pipe":
            pipes.append(resource)

    for ds in datasources:
        content = ds["content"].replace("```", "")
        filename = f"{ds['name']}.datasource"
        generate_datafile(
            content,
            filename=filename,
            data=None,
            _format="ndjson",
            force=True,
            folder=folder,
        )

    for pipe in pipes:
        content = pipe["content"].replace("```", "")
        generate_pipe_file(pipe["name"], content, folder)

    return len(datasources) > 0


def generate_pipe_file(name: str, content: str, folder: str):
    def is_copy(content: str) -> bool:
        return re.search(r"TYPE copy", content, re.IGNORECASE) is not None

    def is_materialization(content: str) -> bool:
        return re.search(r"TYPE materialized", content, re.IGNORECASE) is not None

    def is_sink(content: str) -> bool:
        return re.search(r"TYPE sink", content, re.IGNORECASE) is not None

    if is_copy(content):
        pathname = "copies"
    elif is_materialization(content):
        pathname = "materializations"
    elif is_sink(content):
        pathname = "sinks"
    else:
        pathname = "endpoints"

    base = Path(folder) / pathname
    if not base.exists():
        base = Path()
    f = base / (f"{name}.pipe")
    with open(f"{f}", "w") as file:
        file.write(content)
    click.echo(FeedbackManager.info_file_created(file=f.relative_to(folder)))
