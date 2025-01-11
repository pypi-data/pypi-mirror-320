from __future__ import annotations

import logging
import re
from enum import Enum
from pathlib import Path
from typing import Union

import boto3
from botocore.config import Config
from rich.console import Console

from bedrock_bot.util import sanitize_filename

logger = logging.getLogger()

console = Console()


class ConversationRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

    def __str__(self) -> str:
        return self.value


class _BedrockModel:
    """Base class for all models.

    Usage:
    Add a message to the conversation and invoke the model with `model.invoke(message)`.

    Creating new implementations of this base model:
    - Define extra params to inject to the invoke call on self.model_params
    - Provide a model_id to `super().__init__()`
    """

    name = "Base Model"
    system_prompt: str = "You are a helpful AI assistant."
    _model_id: str
    inference_config: dict = {}
    additional_model_request_fields: dict = {}

    def __init__(
        self,
        boto_config: Union[None, Config] = None,
        system_prompt: Union[None, str] = None,
    ) -> None:
        if not boto_config:
            boto_config = Config()
        self._bedrock = boto3.client("bedrock-runtime", config=boto_config)
        if system_prompt:
            self.system_prompt = system_prompt
        self.messages = []

    def reset(self) -> None:
        self.messages = []

    def append_message(self, role: ConversationRole, message: str, input_files: list[str] = []) -> None:
        content = [{"text": message}]

        for input_file in input_files:
            content.append(self._handle_input_file(input_file))  # noqa: PERF401

        self.messages.append({"role": role.value, "content": content})

    def _handle_input_file(self, input_file: str) -> dict:
        document_extensions = re.compile(r"\.(pdf|csv|doc|docx|xls|xlsx|html|txt|md)$")
        image_extensions = re.compile(r"\.(png|jpeg|jpg|gif|webp)$")
        video_extensions = re.compile(r"\.(mov|mkv|mp4|webm|flv|mpeg|mpg|wmv|three_gp)$")

        file_format = ""
        file_type = ""

        result = document_extensions.search(input_file)
        if result:
            file_format = result.group(1)
            file_type = "document"

        result = image_extensions.search(input_file)
        if result:
            file_format = result.group(1)
            file_type = "image"
            if file_format == "jpg":
                file_format = "jpeg"

        result = video_extensions.search(input_file)
        if result:
            file_format = result.group(1)
            file_type = "video"

        if not file_type:
            msg = f"Unsupported file type: {input_file}"
            raise RuntimeError(msg)

        with Path(input_file).open("rb") as f:
            file_bytes = f.read()

        return {
            file_type: {
                "name": sanitize_filename(input_file),
                "format": file_format,
                "source": {"bytes": file_bytes},
            },
        }

        return {}

    def invoke(self, message: str, input_files: list[str] = []) -> str:
        self.append_message(ConversationRole.USER, message, input_files)

        response = self._invoke()
        self.append_message(ConversationRole.ASSISTANT, response)
        return response

    def _handle_response(self, body: dict) -> str:
        response_message = body["output"]["message"]["content"][0]

        if "text" not in response_message:
            raise RuntimeError("Unexpected response type to prompt: " + response_message["type"])

        return response_message["text"]

    def _invoke(self) -> str:
        with console.status("[bold green]Waiting for response..."):
            logger.info(f"Sending current messages to AI: {self.messages}")
            response = self._bedrock.converse(
                modelId=self._model_id,
                system=[{"text": self.system_prompt}],
                messages=self.messages,
                inferenceConfig=self.inference_config,
                additionalModelRequestFields=self.additional_model_request_fields,
            )
            logger.info(f"Raw response: {response}")

            return self._handle_response(response)
