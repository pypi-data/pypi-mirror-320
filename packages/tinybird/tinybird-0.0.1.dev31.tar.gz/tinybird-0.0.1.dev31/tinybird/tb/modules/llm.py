from copy import deepcopy
from typing import Optional

from tinybird.client import TinyB


class LLM:
    def __init__(
        self,
        user_token: str,
        client: TinyB,
    ):
        self.user_client = deepcopy(client)
        self.user_client.token = user_token

    async def ask(self, system_prompt: str, prompt: Optional[str] = None) -> str:
        """
        Calls the model with the given prompt and returns the response.

        Args:
            system_prompt (str): The system prompt to send to the model.
            prompt (str): The user prompt to send to the model.

        Returns:
            str: The response from the language model.
        """

        data = {"system": system_prompt}

        if prompt:
            data["prompt"] = prompt

        response = await self.user_client._req(
            "/v0/llm",
            method="POST",
            data=data,
        )
        return response.get("result", "")
