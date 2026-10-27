**English** | [简体中文](README.zh-CN.md)

# pico

`pico` is a lightweight local coding agent for code repositories. It runs directly in your terminal, inspects the current workspace first, then uses a set of constrained tools to read files, edit files, and run commands — persisting session state locally under a `.pico/` directory.

Think of it less as a chat window and more as a command-line assistant that keeps working inside your repo. Use it to investigate failing tests, get suggestions based on the actual code structure, or hand it one-off engineering tasks in the current project.

## What it's good for

- Investigating test failures in a local repository
- Reading the current code structure and proposing changes
- Making small, incremental edits grounded in existing files, instead of reasoning in the abstract
- Preserving context across a session so you can resume previous work

## Key features

- Package name: `pico`
- CLI command: `pico`
- Module entry point: `python -m pico`
- Sessions saved under `.pico/sessions/`
- Per-run artifacts saved under `.pico/runs/<run_id>/`

## Screenshots

CLI help output:

![pico help](assets/screenshots/pico-help.png)

Startup screen:

![pico start](assets/screenshots/pico-start.png)

REPL built-in commands and session path:

![pico repl](assets/screenshots/pico-repl.png)

## Installation

Requires Python 3.10+.

If you use `uv`, install dependencies directly:

```bash
uv sync
```

If you're already working in your own Python environment, you can install it in editable mode instead:

```bash
pip install -e .
```

## Quick start

Start interactive mode in the current repository. The default provider is DeepSeek:

```bash
uv run pico
```

Point it at a different working directory:

```bash
uv run pico --cwd /path/to/repo
```

Run a one-off task directly:

```bash
uv run pico "inspect the test failures and propose a fix"
```

If the package is already installed in your current environment, you can also start it this way:

```bash
python -m pico
```

## Common interactive commands

- `/help`: list built-in commands
- `/memory`: view distilled working memory
- `/session`: view the current session file path
- `/reset`: clear the current session state
- `/exit` or `/quit`: exit the REPL
