import sys
from typing import Annotated, Optional

import typer
import litellm
from litellm import completion


app = typer.Typer()


@app.command()
def main(
    prompt: Annotated[str, typer.Argument(help="user message")] = None,
    model: Annotated[str, typer.Argument(help="provider/model")] = "openai/gpt-4o-mini",
    stream: Annotated[bool, typer.Option(help="stream results")] = False,
):
    """
    Interact with language models.
    """
    if not prompt and not sys.stdin.isatty():
        # Read from stdin if no prompt is provided and input is piped
        prompt = sys.stdin.read().strip()
    elif not prompt:
        typer.echo("Error: No prompt provided and no input piped.", err=True)
        raise typer.Exit(code=1)

    messages = [{"role": "user", "content": prompt}]

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
        print(model_response)
        print(model_response.model_dump())

    else:

        response = completion(model=model, messages=messages)
        answer = response.choices[0].message.content
        print(answer)



if __name__ == "__main__":
    app()
