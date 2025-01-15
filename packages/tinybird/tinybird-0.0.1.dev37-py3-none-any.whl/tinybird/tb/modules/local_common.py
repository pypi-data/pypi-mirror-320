import hashlib
import logging
import os
from typing import Optional

import requests

from tinybird.client import TinyB
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.exceptions import CLIException

TB_IMAGE_NAME = "tinybirdco/tinybird-local:beta"
TB_CONTAINER_NAME = "tinybird-local"
TB_LOCAL_PORT = int(os.getenv("TB_LOCAL_PORT", 80))
TB_LOCAL_HOST = f"http://localhost:{TB_LOCAL_PORT}"


async def get_tinybird_local_client(path: Optional[str] = None) -> TinyB:
    """Get a Tinybird client connected to the local environment."""
    config = await get_tinybird_local_config(path)
    return config.get_client(host=TB_LOCAL_HOST)


async def get_tinybird_local_config(path: Optional[str] = None) -> CLIConfig:
    """Craft a client config with a workspace name based on the path of the project files

    It uses the tokens from tinybird local
    """
    config = CLIConfig.get_project_config(path)
    try:
        # ruff: noqa: ASYNC210
        tokens = requests.get(f"{TB_LOCAL_HOST}/tokens").json()
    except Exception:
        raise CLIException("Tinybird local is not running. Please run `tb local start` first.")

    user_token = tokens["user_token"]
    default_token = tokens["workspace_admin_token"]
    # Create a new workspace if path is provided. This is used to isolate the build in a different workspace.
    path = path or os.getcwd()
    if path:
        folder_hash = hashlib.sha256(path.encode()).hexdigest()
        user_client = config.get_client(host=TB_LOCAL_HOST, token=user_token)

        ws_name = f"Tinybird_Local_Build_{folder_hash}"
        logging.debug(f"Workspace used for build: {ws_name}")

        user_workspaces = await user_client.user_workspaces()
        ws = next((ws for ws in user_workspaces["workspaces"] if ws["name"] == ws_name), None)
        if not ws:
            await user_client.create_workspace(ws_name, template=None)
            user_workspaces = await user_client.user_workspaces()
            ws = next((ws for ws in user_workspaces["workspaces"] if ws["name"] == ws_name), None)
            if not ws:
                raise CLIException(f"Workspace {ws_name} not found after creation")

        ws_token = ws["token"]

        config.set_token(ws_token)
        config.set_token_for_host(TB_LOCAL_HOST, ws_token)
        config.set_host(TB_LOCAL_HOST)
    else:
        config.set_token(default_token)
        config.set_token_for_host(TB_LOCAL_HOST, default_token)

    config.set_user_token(user_token)
    return config
