import logging
import os
from pathlib import Path

import click

from tinybird.prompts import mock_prompt
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import CLIException, check_user_token_with_client, coro
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.datafile.fixture import build_fixture_name, persist_fixture
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.llm import LLM
from tinybird.tb.modules.llm_utils import extract_xml
from tinybird.tb.modules.local_common import get_tinybird_local_client


@cli.command()
@click.argument("datasource", type=str)
@click.option("--rows", type=int, default=10, help="Number of events to send")
@click.option(
    "--prompt",
    type=str,
    default="Use the datasource schema to generate sample data",
    help="Extra context to use for data generation",
)
@click.option("--folder", type=str, default=os.getcwd(), help="Folder where datafiles will be placed")
@coro
async def mock(datasource: str, rows: int, prompt: str, folder: str) -> None:
    """Load sample data into a Data Source.

    Args:
        datasource: Path to the datasource file to load sample data into
        rows: Number of events to send
        prompt: Extra context to use for data generation
        folder: Folder where datafiles will be placed
    """

    try:
        datasource_path = Path(datasource)
        datasource_name = datasource
        click.echo(FeedbackManager.highlight(message=f"\n» Creating fixture for {datasource_name}..."))
        if datasource_path.suffix == ".datasource":
            datasource_name = datasource_path.stem
        else:
            datasource_path = Path("datasources", f"{datasource}.datasource")
        datasource_path = Path(folder) / datasource_path

        prompt_path = Path(folder) / "fixtures" / f"{datasource_name}.prompt"
        if not prompt:
            # load the prompt from the fixture.prompt file if it exists
            if prompt_path.exists():
                prompt = prompt_path.read_text()
        else:
            click.echo(FeedbackManager.info(message="* Overriding last prompt..."))
            prompt_path.write_text(prompt)

        datasource_content = datasource_path.read_text()
        config = CLIConfig.get_project_config()
        user_client = config.get_client()
        user_token = config.get_user_token()

        try:
            if not user_token:
                raise CLIException("No user token found")
            await check_user_token_with_client(user_client, token=user_token)
        except Exception:
            click.echo(FeedbackManager.error(message="This action requires authentication. Run 'tb login' first."))
            return
        llm = LLM(user_token=user_token, host=user_client.host)
        tb_client = await get_tinybird_local_client(os.path.abspath(folder))
        prompt = f"<datasource_schema>{datasource_content}</datasource_schema>\n<user_input>{prompt}</user_input>"
        response = llm.ask(system_prompt=mock_prompt(rows), prompt=prompt)
        sql = extract_xml(response, "sql")
        if os.environ.get("TB_DEBUG", "") != "":
            logging.debug(sql)
        result = await tb_client.query(f"{sql} FORMAT JSON")
        data = result.get("data", [])[:rows]
        fixture_name = build_fixture_name(datasource_path.absolute().as_posix(), datasource_name, datasource_content)
        persist_fixture(fixture_name, data, folder)
        click.echo(FeedbackManager.success(message=f"✓ /fixtures/{fixture_name}.ndjson created with {rows} rows"))

    except Exception as e:
        raise CLIException(FeedbackManager.error_exception(error=e))
