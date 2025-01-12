from datetime import datetime
import sys
from typing import Annotated, Optional

import litellm
from litellm import completion
from litellm import completion_cost
import rich
from rich.console import Console
from rich.table import Table
import typer


app = typer.Typer(add_completion=False)


def get_piped_text() -> str | None:
    piped_text = None
    if not sys.stdin.isatty():
        piped_text = sys.stdin.read().strip()
    return piped_text


def get_user_message_content(
    prompt: str, piped_text: str, piped_placeholder: str
) -> str:

    if piped_text is None and prompt is None:
        print("Error: No input piped and no prompt provided.")
        raise typer.Exit(code=1)
    elif piped_text is None and prompt is not None:
        msg = prompt
    elif piped_text is not None and prompt is None:
        msg = piped_text
    elif piped_text is not None and prompt is not None:
        if piped_placeholder not in prompt:
            print(
                f"Error: Piped input provided but '{piped_placeholder}' "
                "placeholder is missing from prompt."
            )
            raise typer.Exit(code=1)
        else:
            msg = prompt.replace(piped_placeholder, piped_text)
            msg = msg.replace("\\n", "\n")

    return msg


@app.command()
def main(
    prompt: Annotated[
        str,
        typer.Option(
            "--prompt",
            "-p",
            help="user message. @pipe will be replaced with piped input",
        ),
    ] = None,
    model: Annotated[
        str, typer.Option("--model", "-m", help="provider/model")
    ] = "openai/gpt-4o-mini",
    temperature: Annotated[
        float, typer.Option("--temperature", "-t", help="temperature")
    ] = 0.7,
    piped_placeholder: Annotated[
        str, typer.Option(help="replace this string in prompt with piped input")
    ] = "@pipe",
    stream: Annotated[
        bool, typer.Option("--stream", "-s", help="stream results")
    ] = False,
    dryrun: Annotated[bool, typer.Option(help="dry run")] = False,
    metrics: Annotated[bool, typer.Option(help="show metrics")] = False,
):
    """Examples

    example 1 (hello):

    > lmc -p hello



    example 2 (cat file and @pipe replacement):

    > cat <file_name> | lmc -p "Summarize the following text: @pipe"
    """

    piped_text = get_piped_text()
    user_message_content = get_user_message_content(
        prompt, piped_text, piped_placeholder
    )

    if dryrun:
        rich.print(f"piped_text={piped_text}")
        rich.print(f"prompt={prompt}")
        rich.print(f"user_message_content={user_message_content}")
        raise typer.Exit(code=0)

    messages = [{"role": "user", "content": user_message_content}]

    start = datetime.now()

    if stream:

        stream_response = completion(
            model=model, messages=messages, temperature=temperature, stream=True
        )
        cached_chunks = []
        for chunk in stream_response:
            cached_chunks.append(chunk)
            if "choices" in chunk and chunk["choices"]:
                delta = chunk["choices"][0].get("delta", {}).get("content", "")
                if delta is not None:
                    print(delta, end="", flush=True)
        print()
        model_response = litellm.stream_chunk_builder(cached_chunks, messages=messages)

    else:

        model_response = completion(
            model=model, messages=messages, temperature=temperature
        )
        answer = model_response.choices[0].message.content
        print(answer)

    end = datetime.now()

    if metrics:
        table = Table()
        table.add_column("Start")
        table.add_column("End")
        table.add_column("Duration (s)")
        table.add_column("Cost")
        cost = "${:,.5f}".format(completion_cost(completion_response=model_response))
        duration = "{:,.2f}".format((end - start).total_seconds())
        table.add_row(start.isoformat(), end.isoformat(), duration, cost)
        console = Console()
        console.print(table)


if __name__ == "__main__":
    app()
