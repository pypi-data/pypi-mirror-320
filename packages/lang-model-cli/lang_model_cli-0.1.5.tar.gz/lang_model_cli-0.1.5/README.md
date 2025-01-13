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

Full usage instructions can be viewed using,
```bash
lmc --help
```

Here are the basics.


## user message with  `--prompt` or `-p`

```bash
lmc -p "briefly describe cosmology"
```

## stream output with  `--stream` or `-s`

```bash
lmc -p "briefly describe cosmology" -s
```

## system message with  `--system` or `-y`

```bash
lmc -p "briefly describe cosmology" -s -y "speak like a pirate"
```

## user message with pipe

```bash
cat <filename> | lmc
```

If text is piped in and there is no `-p` option then the piped input will become the user message content.

## user message with pipe and `-p`

```bash
cat <filename> | lmc -p "Summarize the following text: @pipe"
```

In this case, the `@pipe` string will be replaced with the piped in text.
This could also be accomplished using [command substitution](https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html),

```bash
lmc -p "Summarize the following text: $(cat <filename>)"
```
