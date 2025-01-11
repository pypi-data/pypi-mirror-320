import sys

from typing_extensions import Annotated

from rich import print
from rich.panel import Panel
from typer import Argument, Option, Typer

from arkhos.base_handler import base_handler

app = Typer(add_completion=False)


@app.command(
    epilog="""
Examples:

    arkhos\n
    arkhos GET --path "/hello" --get name=james&age=33\n
    arkhos POST --body '{"name": "james"}' --headers '{"Content-Type": "application/json"}'\n
    arkhos EMAIL --subject "Hello" --body "This is a test email"\n
"""
)
def main(
    method: Annotated[
        str, Argument(help="Arkhos request type: GET, POST, CRON, EMAIL")
    ] = "GET",
    get: Annotated[str, Option(help="?key_1=value_1&key_2=value_2")] = "",
    path: Annotated[str, Option(help="/path/to/thing")] = "/",
    body: Annotated[str, Option(help='"the HTTP request or email body"')] = "",
    headers: Annotated[str, Option(help="{'key_1': 'value_1', ...}")] = "",
    subject: Annotated[str, Option(help='"the email subject"')] = "",
):
    """Test your Arkhos app locally."""
    response = base_handler(
        {
            "method": method,
            "path": path,
            "GET": parse_local_get_parameters(get),
            "body": body,
        }
    )
    body = response.get("body", "")
    status = response.get("status")
    status_color = "green" if status == 200 else "red"
    if not sys.stdout.isatty():
        print(body)
    else:
        print(
            Panel(
                body,
                title=f"[purple]{method.upper()} [{status_color}]{status}",
                title_align="left",
                subtitle="[purple]Arkhos",
                subtitle_align="right",
            )
        )


def parse_local_get_parameters(parameters_string: str) -> dict:
    """
    input (from the command line): ?name=james&age=33
    returns: {
        "name": "james",
        "age": 33
    }

    questions
        - url encoding/decoding
        - data types
    """

    if len(parameters_string) == 0:
        return {}

    if parameters_string[0] == "?":
        parameters_string = parameters_string[1:]

    # "name=james"
    get_parameters = {}
    kv_strings = parameters_string.split("&")
    for kv_string in kv_strings:
        get_key, get_value = kv_string.split("=")
        get_parameters[get_key] = get_value

    return get_parameters
