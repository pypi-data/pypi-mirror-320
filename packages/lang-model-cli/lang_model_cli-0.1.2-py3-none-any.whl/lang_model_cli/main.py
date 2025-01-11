import sys
from typing import Annotated, Optional

import litellm
from litellm import completion
import rich
import typer


app = typer.Typer(add_completion=False)


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
    piped_placeholder: Annotated[
        str, typer.Option(help="replace this string in prompt with piped input")
    ] = "@pipe",
    stream: Annotated[
        bool, typer.Option("--stream", "-s", help="stream results")
    ] = False,
    dryrun: Annotated[bool, typer.Option(help="dry run")] = False,
):
    """
    Interact with language models.
    """

    piped_text = None
    if not sys.stdin.isatty():
        piped_text = sys.stdin.read().strip()

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

    if dryrun:
        rich.print(msg)
        raise typer.Exit(code=0)

    messages = [{"role": "user", "content": msg}]

    if stream:

        stream_response = completion(model=model, messages=messages, stream=True)
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

        model_response = completion(model=model, messages=messages)
        answer = model_response.choices[0].message.content
        print(answer)


if __name__ == "__main__":
    app()
