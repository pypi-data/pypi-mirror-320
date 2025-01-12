# Lang Model CLI

A command line interface for interacting with large language models.


# Quick Start

## Install with pip
```bash
pip install lang-model-cli
```

## Export provider API keys
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."
...
```

## Use the CLI

You can construct user messages in several ways.

Pass in a prompt directly,
```bash
lmc -p hello
```

Pipe input in,
```bash
cat <filename> | lmc
```

Or combine the two,
```bash
cat <filename> | lmc -p "Explain the following text: @pipe"
```
Here `@pipe` will be replaced with the contents of `<filename>`.
