from os import getenv
from typing import Union, Dict, List

from httpx import Response

from ethosian.api.api import api, invalid_response
from ethosian.api.routes import ApiRoutes
from ethosian.api.schemas.assistant import (
    AssistantEventCreate,
    AssistantRunCreate,
)
from ethosian.constants import ethosian_API_KEY_ENV_VAR, ethosian_WS_KEY_ENV_VAR
from ethosian.cli.settings import ethosian_cli_settings
from ethosian.utils.log import logger


def create_assistant_run(run: AssistantRunCreate) -> bool:
    if not ethosian_cli_settings.api_enabled:
        return True

    logger.debug("--o-o-- Creating Assistant Run")
    with api.AuthenticatedClient() as api_client:
        try:
            r: Response = api_client.post(
                ApiRoutes.ASSISTANT_RUN_CREATE,
                headers={
                    "Authorization": f"Bearer {getenv(ethosian_API_KEY_ENV_VAR)}",
                    "ethosian-WORKSPACE": f"{getenv(ethosian_WS_KEY_ENV_VAR)}",
                },
                json={
                    "run": run.model_dump(exclude_none=True),
                    # "workspace": assistant_workspace.model_dump(exclude_none=True),
                },
            )
            if invalid_response(r):
                return False

            response_json: Union[Dict, List] = r.json()
            if response_json is None:
                return False

            logger.debug(f"Response: {response_json}")
            return True
        except Exception as e:
            logger.debug(f"Could not create assistant run: {e}")
    return False


def create_assistant_event(event: AssistantEventCreate) -> bool:
    if not ethosian_cli_settings.api_enabled:
        return True

    logger.debug("--o-o-- Creating Assistant Event")
    with api.AuthenticatedClient() as api_client:
        try:
            r: Response = api_client.post(
                ApiRoutes.ASSISTANT_EVENT_CREATE,
                headers={
                    "Authorization": f"Bearer {getenv(ethosian_API_KEY_ENV_VAR)}",
                    "ethosian-WORKSPACE": f"{getenv(ethosian_WS_KEY_ENV_VAR)}",
                },
                json={
                    "event": event.model_dump(exclude_none=True),
                    # "workspace": assistant_workspace.model_dump(exclude_none=True),
                },
            )
            if invalid_response(r):
                return False

            response_json: Union[Dict, List] = r.json()
            if response_json is None:
                return False

            logger.debug(f"Response: {response_json}")
            return True
        except Exception as e:
            logger.debug(f"Could not create assistant event: {e}")
    return False
