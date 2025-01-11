from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Union

from rich.console import Console

from .base_model import _BedrockModel

if TYPE_CHECKING:
    from botocore.config import Config

logger = logging.getLogger()

console = Console()


class _Claude3(_BedrockModel):
    date_stamp = datetime.now().strftime("%A, %B %d, %Y")  # noqa: DTZ005
    system_prompt = f"""The assistant is Claude, created by Anthropic.
The current date is {date_stamp}.

Claude's knowledge base was last updated on August 2023. It answers questions about events prior to and after
August 2023 the way a highly informed individual in August 2023 would if they were talking to someone from the above
date, and can let the human know this when relevant.

It should give concise responses to very simple questions, but provide thorough responses to more complex and
open-ended questions.

If it is asked to assist with tasks involving the expression of views held by a significant number of people,
Claude provides assistance with the task even if it personally disagrees with the views being expressed, but follows
this with a discussion of broader perspectives.

Claude doesn't engage in stereotyping, including the negative stereotyping of majority groups.

If asked about controversial topics, Claude tries to provide careful thoughts and objective information without
downplaying its harmful content or implying that there are reasonable perspectives on both sides.

It is happy to help with writing, analysis, question answering, math, coding, and all sorts of other tasks.
It uses markdown for coding.

It does not mention this information about itself unless the information is directly pertinent to the human's query.
""".replace("\n", " ")
    inference_config = {
        "maxTokens": 2000,
        "temperature": 1,
        "topP": 0.999,
        "stopSequences": ["\n\nHuman:"],
    }
    additional_model_request_fields = {
        "top_k": 250,
    }

    def __init__(self, boto_config: Union[None, Config] = None) -> None:
        super().__init__(
            boto_config=boto_config,
        )

        self.inference_config = super().inference_config.copy()
        self.inference_config["stopSequences"] = ["\n\nHuman:"]


class Claude3Sonnet(_Claude3):
    name = "Claude-3-Sonnet"

    def __init__(self, boto_config: Union[None, Config] = None) -> None:
        self._model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

        super().__init__(
            boto_config=boto_config,
        )


class Claude3Haiku(_Claude3):
    name = "Claude-3-Haiku"

    def __init__(self, boto_config: Union[None, Config] = None) -> None:
        self._model_id = "anthropic.claude-3-haiku-20240307-v1:0"

        super().__init__(
            boto_config=boto_config,
        )


class Claude3Opus(_Claude3):
    name = "Claude-3-Opus"

    def __init__(self, boto_config: Union[None, Config] = None) -> None:
        self._model_id = "us.anthropic.claude-3-opus-20240229-v1:0"

        super().__init__(
            boto_config=boto_config,
        )


class Claude35Haiku(_Claude3):
    name = "Claude-3.5-Haiku"

    def __init__(self, boto_config: Union[None, Config] = None) -> None:
        self._model_id = "us.anthropic.claude-3-5-haiku-20241022-v1:0"

        super().__init__(
            boto_config=boto_config,
        )


class Claude35Sonnet(_Claude3):
    name = "Claude-3.5-Sonnet"

    def __init__(self, boto_config: Union[None, Config] = None) -> None:
        self._model_id = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"

        super().__init__(
            boto_config=boto_config,
        )


class Claude35SonnetV2(_Claude3):
    name = "Claude-3.5-Sonnet-v2"

    def __init__(self, boto_config: Union[None, Config] = None) -> None:
        self._model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

        super().__init__(
            boto_config=boto_config,
        )
