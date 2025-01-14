import os
import re
from os import getcwd
from pathlib import Path
from typing import Optional

import click

from tinybird.client import TinyB
from tinybird.prompts import create_prompt, mock_prompt
from tinybird.tb.modules.cicd import init_cicd
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import _generate_datafile, check_user_token_with_client, coro, generate_datafile
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.datafile.fixture import build_fixture_name, persist_fixture
from tinybird.tb.modules.exceptions import CLIException
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.llm import LLM
from tinybird.tb.modules.llm_utils import extract_xml, parse_xml
from tinybird.tb.modules.local_common import get_tinybird_local_client


@cli.command()
@click.option(
    "--data",
    type=click.Path(exists=True),
    default=None,
    help="Initial data to be used to create the project",
)
@click.option(
    "--prompt",
    type=str,
    default=None,
    help="Prompt to be used to create the project",
)
@click.option(
    "--folder",
    default=".",
    type=click.Path(exists=False, file_okay=False),
    help="Folder where datafiles will be placed",
)
@click.option("--rows", type=int, default=10, help="Number of events to send")
@coro
async def create(
    data: Optional[str],
    prompt: Optional[str],
    folder: Optional[str],
    rows: int,
) -> None:
    """Initialize a new project."""
    folder = folder or getcwd()
    folder_path = Path(folder)
    if not folder_path.exists():
        folder_path.mkdir()

    try:
        config = CLIConfig.get_project_config(folder)
        tb_client = config.get_client()
        user_token: Optional[str] = None
        if prompt:
            try:
                user_token = config.get_user_token()
                if not user_token:
                    raise CLIException("No user token found")
                await check_user_token_with_client(tb_client, token=user_token)
            except Exception as e:
                click.echo(
                    FeedbackManager.error(
                        message=f"This action requires authentication. Run 'tb login' first. Error: {e}"
                    )
                )
                return
        local_client = await get_tinybird_local_client(folder)

        if not validate_project_structure(folder):
            click.echo(FeedbackManager.highlight(message="\n» Creating new project structure..."))
            create_project_structure(folder)
            click.echo(FeedbackManager.success(message="✓ Scaffolding completed!\n"))

        click.echo(FeedbackManager.highlight(message="\n» Creating resources..."))
        datasources_created = await create_resources(local_client, tb_client, user_token, data, prompt, folder)
        click.echo(FeedbackManager.success(message="✓ Done!\n"))

        if not already_has_cicd(folder):
            click.echo(FeedbackManager.highlight(message="\n» Creating CI/CD files for GitHub and GitLab..."))
            init_git(folder)
            await init_cicd(data_project_dir=os.path.relpath(folder))
            click.echo(FeedbackManager.success(message="✓ Done!\n"))

        if validate_fixtures(folder) and datasources_created:
            click.echo(FeedbackManager.highlight(message="\n» Generating fixtures..."))

            if data:
                ds_name = os.path.basename(data.split(".")[0])
                data_content = Path(data).read_text()
                datasource_path = Path(folder) / "datasources" / f"{ds_name}.datasource"
                fixture_name = build_fixture_name(
                    datasource_path.absolute().as_posix(), ds_name, datasource_path.read_text()
                )
                click.echo(FeedbackManager.info(message=f"✓ /fixtures/{ds_name}"))
                persist_fixture(fixture_name, data_content, folder)
            elif prompt and user_token:
                datasource_files = [f for f in os.listdir(Path(folder) / "datasources") if f.endswith(".datasource")]
                for datasource_file in datasource_files:
                    datasource_path = Path(folder) / "datasources" / datasource_file
                    llm = LLM(user_token=user_token, host=tb_client.host)
                    datasource_name = datasource_path.stem
                    datasource_content = datasource_path.read_text()
                    has_json_path = "`json:" in datasource_content
                    if has_json_path:
                        prompt = f"<datasource_schema>{datasource_content}</datasource_schema>\n<user_input>{prompt}</user_input>"
                        response = llm.ask(system_prompt=mock_prompt(rows), prompt=prompt)
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


PROJECT_PATHS = ("datasources", "endpoints", "materializations", "copies", "sinks", "fixtures", "tests")


def validate_project_structure(folder: str) -> bool:
    return all((Path(folder) / path).exists() for path in PROJECT_PATHS)


def validate_fixtures(folder: str) -> bool:
    datasource_files = [f for f in os.listdir(Path(folder) / "datasources") if f.endswith(".datasource")]
    return len(datasource_files) > 0


def already_has_cicd(folder: str) -> bool:
    ci_cd_paths = (".gitlab", ".github")
    return any((Path(folder) / path).exists() for path in ci_cd_paths)


def create_project_structure(folder: str):
    folder_path = Path(folder)
    for x in PROJECT_PATHS:
        try:
            f = folder_path / x
            f.mkdir()
        except FileExistsError:
            pass
        click.echo(FeedbackManager.info_path_created(path=x))


async def create_resources(
    local_client: TinyB,
    tb_client: TinyB,
    user_token: Optional[str],
    data: Optional[str],
    prompt: Optional[str],
    folder: str,
):
    force = True
    folder_path = Path(folder)
    if data:
        path = folder_path / data
        format = path.suffix.lstrip(".")
        await _generate_datafile(str(path), local_client, format=format, force=force)
        name = data.split(".")[0]
        generate_pipe_file(
            f"{name}_endpoint",
            f"""
NODE endpoint
SQL >
    SELECT * from {name}
TYPE ENDPOINT
            """,
            folder,
        )
        return True
    elif prompt and user_token:
        datasource_paths = [
            Path(folder) / "datasources" / f
            for f in os.listdir(Path(folder) / "datasources")
            if f.endswith(".datasource")
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
        llm = LLM(user_token=user_token, host=tb_client.host)
        result = llm.ask(system_prompt=create_prompt(resources_xml), prompt=prompt)
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
                force=force,
                folder=folder,
            )

        for pipe in pipes:
            content = pipe["content"].replace("```", "")
            generate_pipe_file(pipe["name"], content, folder)

        return len(datasources) > 0


def init_git(folder: str):
    try:
        path = Path(folder)
        gitignore_file = path / ".gitignore"

        if gitignore_file.exists():
            content = gitignore_file.read_text()
            if ".tinyb" not in content:
                gitignore_file.write_text(content + "\n.tinyb\n")
        else:
            gitignore_file.write_text(".tinyb\n")

        click.echo(FeedbackManager.info_file_created(file=".gitignore"))
    except Exception as e:
        raise CLIException(f"Error initializing Git: {e}")


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
