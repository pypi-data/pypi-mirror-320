from __future__ import annotations

import logging
import readline  # noqa: F401 # pylint: disable=unused-import
import sys
from typing import TYPE_CHECKING

import boto3
import click
from botocore.config import Config

from . import model_list
from .util import formatted_print

if TYPE_CHECKING:
    from bedrock_bot.models.base_model import _BedrockModel

CONTEXT_SETTINGS = {"help_option_names": ["--help", "-h"]}
LOG_FORMATTER = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    "%Y-%m-%d %H:%M:%S",
)
log = None


def configure_logger(*, verbose: bool) -> None:
    global log  # noqa: PLW0603
    log_level = logging.ERROR
    if verbose:
        log_level = logging.INFO

    logging.basicConfig(level=log_level)
    log = logging.getLogger()
    log.handlers[0].setFormatter(LOG_FORMATTER)
    log.info(f"Log level set to {logging.getLevelName(log_level)}")


def available_models() -> list[str]:
    return [x.name for x in model_list]


def model_class_from_input(value: str) -> type[_BedrockModel]:
    try:
        return next(x for x in model_list if x.name.lower() == value.lower())
    except StopIteration as err:
        msg = f"Invalid value: {value}. Allowed values are: {available_models}"
        raise click.BadParameter(msg) from err


def generate_boto_config(region: str) -> Config:
    boto_config = Config()
    if region:
        boto_config = Config(region_name=region, read_timeout=600)
    elif boto3.setup_default_session() and not boto3.DEFAULT_SESSION.region_name:
        boto_config = Config(region_name="us-east-1")
    return boto_config


def get_user_input() -> str:
    if not sys.stdin.isatty():
        print("Note that stdin is not supported for input")  # noqa: T201
        sys.exit()
    else:
        return input("> ")


def handle_args(args: list[str]) -> str:
    user_input = " ".join(args)
    print(f"> {user_input}", file=sys.stderr)  # noqa: T201
    return user_input


def handle_user_input(
    instance: _BedrockModel,
    user_input: str,
    input_files: list[str],
    *,
    raw_output: bool,
) -> None:
    response = instance.invoke(user_input, input_files)

    if raw_output:
        print(response)  # noqa: T201
    else:
        formatted_print(response)


@click.command()
@click.argument("args", nargs=-1)
@click.option(
    "-r",
    "--region",
    help="The AWS region to use for requests. If no default region is specified, defaults to us-east-1",
)
@click.option("--raw-output", is_flag=True, default=False, help="Don't interpret markdown in the AI response")
@click.option(
    "-m",
    "--model",
    type=click.Choice(available_models(), case_sensitive=False),
    default="Nova-Lite",
    help="The model to use for requests",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose logging messages",
)
@click.option(
    "-i",
    "--input-file",
    "input_files",
    multiple=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Read in file(s) to be used in your queries",
)
@click.option("--system-prompt", help="Provide a custom system prompt to override the default")
def main(  # noqa: PLR0913
    *,
    model: str,
    region: str,
    raw_output: bool,
    args: list[str],
    verbose: bool,
    input_files: list[str],
    system_prompt: str,
) -> None:
    configure_logger(verbose=verbose)

    model_class = model_class_from_input(model)
    boto_config = generate_boto_config(region)
    instance = model_class(boto_config=boto_config)

    if system_prompt:
        instance.system_prompt = system_prompt

    if args:
        user_input = handle_args(args)
        handle_user_input(instance, user_input, input_files, raw_output=raw_output)
        sys.exit(0)

    print(  # noqa: T201
        f"Hello! I am an AI assistant powered by Amazon Bedrock and using the model {instance.name}. "
        "Enter 'quit' or 'exit' at any time to exit. How may I help you today?",
    )
    print(  # noqa: T201
        "(You can clear existing context by starting a query with 'new>' or 'reset>')",
    )

    first_iteration = True
    while True:
        print()  # noqa: T201
        try:
            user_input = get_user_input()
        except KeyboardInterrupt:
            if instance.messages:
                print("\nCtrl+c detected. Resetting conversation...")  # noqa: T201
                instance.reset()
                continue

            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() == "quit" or user_input.lower() == "exit":
            print("\nGoodbye!")  # noqa: T201
            sys.exit()
        if user_input.lower().startswith("new>") or user_input.lower().startswith(
            "reset>",
        ):
            print("\nResetting conversation...")  # noqa: T201
            instance.reset()
            continue

        handle_user_input(instance, user_input, input_files, raw_output=raw_output)
        if first_iteration:
            first_iteration = False
            input_files = []
