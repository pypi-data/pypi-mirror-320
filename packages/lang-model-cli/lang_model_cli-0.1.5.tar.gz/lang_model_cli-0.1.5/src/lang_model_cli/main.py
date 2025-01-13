from datetime import datetime
import sqlite3
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


def initialize_db(db_path: str):
    """Initialize the SQLite database and create tables if they do not exist."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_dt TEXT,
                end_dt TEXT,
                prompt TEXT,
                response TEXT,
                model TEXT,
                temperature REAL,
                cost REAL,
                duration REAL
            )
            """
        )
        conn.commit()


def log_to_db(
    db_path, start_dt, end_dt, prompt, response, model, temperature, cost, duration
):
    """Log response data to the database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO completions (start_dt, end_dt, prompt, response, model, temperature, cost, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                start_dt.isoformat(),
                end_dt.isoformat(),
                prompt,
                response,
                model,
                temperature,
                cost,
                duration,
            ),
        )
        conn.commit()


@app.command()
def main(
    prompt: Annotated[
        str | None,
        typer.Option(
            "--prompt",
            "-p",
            help="user message. @pipe will be replaced with piped input",
        ),
    ] = None,
    system: Annotated[
        str | None,
        typer.Option(
            "--system",
            "-y",
            help="system message",
        ),
    ] = None,
    model: Annotated[
        str, typer.Option("--model", "-m", help="provider/model")
    ] = "openai/gpt-4o-mini",
    temperature: Annotated[
        float, typer.Option("--temperature", "-t", help="temperature")
    ] = 0.7,
    user: Annotated[str, typer.Option(help="user name for logging")] = "default",
    db_path: Annotated[str, typer.Option(help="path to sqlite db")] = "lmc_logs.db",
    piped_placeholder: Annotated[
        str, typer.Option(help="replace this string in prompt with piped input")
    ] = "@pipe",
    stream: Annotated[
        bool, typer.Option("--stream", "-s", help="stream results")
    ] = False,
    dryrun: Annotated[bool, typer.Option(help="dry run")] = False,
    show_metrics: Annotated[bool, typer.Option(help="show metrics")] = False,
    show_response: Annotated[bool, typer.Option(help="show full response")] = False,
):
    """Examples

    example 1 (hello):

    > lmc -p hello



    example 2 (cat file and @pipe replacement):

    > cat <file_name> | lmc -p "Summarize the following text: @pipe"
    """

    initialize_db(db_path)

    piped_text = get_piped_text()
    user_message_content = get_user_message_content(
        prompt, piped_text, piped_placeholder
    )

    messages = []
    if system is not None:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user_message_content})

    if dryrun:
        rich.print(f"piped_text={piped_text}")
        rich.print(f"prompt={prompt}")
        rich.print(f"system={system}")
        rich.print(f"messages={messages}")
        raise typer.Exit(code=0)

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
        response_text = model_response.choices[0].message.content

    else:

        model_response = completion(
            model=model, messages=messages, temperature=temperature
        )
        response_text = model_response.choices[0].message.content
        print(response_text)

    end = datetime.now()
    duration = end - start
    if model.startswith("ollama"):
        cost = 0
    else:
        cost = completion_cost(completion_response=model_response)

    if show_response:
        rich.print(model_response)

    if show_metrics:
        table = Table()
        table.add_column("Start")
        table.add_column("End")
        table.add_column("Duration (s)")
        table.add_column("Cost")

        duration_str = "{:,.2f}".format(duration.total_seconds())
        cost_str = "${:,.5f}".format(cost)
        table.add_row(start.isoformat(), end.isoformat(), duration_str, cost_str)
        console = Console()
        console.print(table)

    log_to_db(
        db_path,
        start,
        end,
        prompt,
        response_text,
        model,
        temperature,
        cost,
        duration.total_seconds(),
    )


def main():
    app()


if __name__ == "__main__":
    main()
