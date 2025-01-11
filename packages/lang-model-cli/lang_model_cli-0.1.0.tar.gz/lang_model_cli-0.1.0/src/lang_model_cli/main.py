import sys
from typing import Annotated, Optional

import typer
from litellm import completion


app = typer.Typer()


@app.command()
def main(
    prompt: Annotated[str, typer.Argument(help="user message")] = None,
    model: Annotated[str, typer.Argument(help="provider/model")] = "openai/gpt-4o-mini",
):
    """
    Interact with the specified LLM model using the provided prompt or piped input.
    """
    if not prompt and not sys.stdin.isatty():
        # Read from stdin if no prompt is provided and input is piped
        prompt = sys.stdin.read().strip()
    elif not prompt:
        typer.echo("Error: No prompt provided and no input piped.", err=True)
        raise typer.Exit(code=1)

    messages = [{"role": "user", "content": prompt}]
    try:
        response = completion(model=model, messages=messages)
        answer = response.choices[0].message.content
        typer.echo(answer)
    except Exception as e:
        typer.echo(f"An error occurred: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
