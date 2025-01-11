import re
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

console = Console()


def formatted_print(text: str) -> None:
    console.print(Markdown(text, code_theme="material"))


def sanitize_filename(file_name: str) -> str:
    allowed_chars = r"[\w\s\-\(\) \[\]]"

    sanitized_filename = Path(file_name).name
    sanitized_filename = re.sub(r"\.[^\.]*$", "", sanitized_filename)
    sanitized_filename = re.sub(f"[^{allowed_chars}]", " ", sanitized_filename)
    sanitized_filename = re.sub(r"\.", " ", sanitized_filename)
    sanitized_filename = re.sub(r"\s{2,}", " ", sanitized_filename)

    return sanitized_filename  # noqa: RET504
