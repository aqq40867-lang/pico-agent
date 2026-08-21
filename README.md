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
- Supports four model backends:
  - Ollama
  - OpenAI-compatible Responses API
  - Anthropic-compatible Messages API
  - DeepSeek Anthropic-compatible API

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

## Model backends

Pico reads `.env` from the project root on startup. Keep real keys in `.env`; the repository only ships `.env.example`. Configuration priority is:

```text
explicit CLI flags > PICO_* variables in .env > legacy environment variables > code defaults
```

Provider selection order specifically is:

```text
--provider > PICO_PROVIDER > code default (deepseek)
```

When neither `--provider` nor `PICO_PROVIDER` is set, it defaults to `deepseek`. This is the recommended configuration path: DeepSeek's Anthropic-compatible endpoint depends on less local model setup than Ollama, and assumes one less default-gateway layer than the OpenAI-compatible/Anthropic-compatible proxies. The other providers remain fully supported — set `PICO_PROVIDER=openai`, `PICO_PROVIDER=anthropic`, or `PICO_PROVIDER=ollama` in `.env`, or pass `--provider openai`, `--provider anthropic`, or `--provider ollama` explicitly.

`.env` is loaded before the provider client is built, and overrides any same-named variable already in the process environment. The model name and base URL can be overridden per-run with `--model` and `--base-url`; API keys are only ever read from environment variables.

First-time local setup:

```bash
cp .env.example .env
```

Then fill in the key for whichever provider you plan to use. `.env` is already covered by `.gitignore` — do not commit real keys.

### Recommended: DeepSeek

The minimal configuration only needs a key:

```bash
PICO_DEEPSEEK_API_KEY="your-api-key"
```

The default model and endpoint are:

```bash
PICO_DEEPSEEK_API_BASE="https://api.deepseek.com/anthropic"
PICO_DEEPSEEK_MODEL="deepseek-v4-pro"
```

So in the common case, filling in just `PICO_DEEPSEEK_API_KEY` in `.env` is enough to start:

```bash
uv run pico
```

If you need to switch models or the proxy address temporarily, you don't need to edit `.env` — override directly:

```bash
uv run pico --model deepseek-v4-pro --base-url https://api.deepseek.com/anthropic
```

DeepSeek currently uses the Anthropic-compatible Messages API, so the runtime reuses the Anthropic-compatible client under the hood; this only affects the HTTP protocol, not the CLI usage.

Pico currently uses a text-encoded tool protocol, so it explicitly disables provider-native thinking on DeepSeek requests, to avoid thinking content consuming the per-step output budget or producing thinking blocks that can't be replayed. If native tool-calling is adopted later, full replay of thinking blocks needs to be implemented alongside it — this switch can't simply be removed on its own.

### Optional: right.codes

right.codes offers two optional provider paths in Pico:

- `--provider openai`: uses the OpenAI-compatible `/responses` API, default base URL `https://www.right.codes/codex/v1`, default model `gpt-5.4`
- `--provider anthropic`: uses the Anthropic-compatible `/messages` API, default base URL `https://www.right.codes/claude/v1`, default model `claude-sonnet-4-6`

If right.codes gave you a shared key, it's recommended to fill in just this one:

```bash
PICO_RIGHT_CODES_API_KEY="your-right-codes-key"
```

Then choose a provider as needed:

```bash
uv run pico --provider openai
uv run pico --provider anthropic
```

If you'd rather keep the keys for the two providers explicitly separate, you can configure them individually:

```bash
PICO_OPENAI_API_KEY="your-right-codes-key-for-codex"
PICO_ANTHROPIC_API_KEY="your-right-codes-key-for-claude"
```

Don't write shell-expansion forms like `PICO_OPENAI_API_KEY=$PICO_RIGHT_CODES_API_KEY` in `.env` — Pico's `.env` parser only reads literal values and does not expand variable references. Either set `PICO_RIGHT_CODES_API_KEY` alone, or fill the key string into each provider-specific variable separately.

If a request to right.codes returns "API Key额度不足" (insufficient quota), that means the protocol and endpoint are wired up correctly, but the current key has no remaining quota — swap in a key with quota, or top up on the right.codes dashboard.

Current provider environment variables:

| provider | base URL | API key | model |
| --- | --- | --- | --- |
| `deepseek` | `PICO_DEEPSEEK_API_BASE`, falls back to `DEEPSEEK_API_BASE`, default `https://api.deepseek.com/anthropic` | `PICO_DEEPSEEK_API_KEY`, falls back to `DEEPSEEK_API_KEY` | `PICO_DEEPSEEK_MODEL`, falls back to `DEEPSEEK_MODEL`, default `deepseek-v4-pro` |
| `openai` | `PICO_OPENAI_API_BASE`, falls back to `OPENAI_API_BASE`, default `https://www.right.codes/codex/v1` | `PICO_OPENAI_API_KEY`, falls back to `OPENAI_API_KEY`, `PICO_RIGHT_CODES_API_KEY`, `RIGHT_CODES_API_KEY`, `PICO_ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY` | `PICO_OPENAI_MODEL`, falls back to `OPENAI_MODEL`, default `gpt-5.4` |
| `anthropic` | `PICO_ANTHROPIC_API_BASE`, falls back to `ANTHROPIC_API_BASE`, default `https://www.right.codes/claude/v1` | `PICO_ANTHROPIC_API_KEY`, falls back to `ANTHROPIC_API_KEY`, `PICO_RIGHT_CODES_API_KEY`, `RIGHT_CODES_API_KEY`, `PICO_OPENAI_API_KEY`, `OPENAI_API_KEY` | `PICO_ANTHROPIC_MODEL`, falls back to `ANTHROPIC_MODEL`, default `claude-sonnet-4-6` |
| `ollama` | `--host`, default `http://127.0.0.1:11434` | not required | `--model`, default `qwen3.5:4b` |

If you have additional sensitive environment variables that need to be redacted from traces and reports, configure a comma-separated list of names via `PICO_SECRET_ENV_NAMES`, or pass `--secret-env-name NAME` repeatedly at startup.

### OpenAI-compatible endpoint

To switch to an OpenAI-compatible `/responses` service, pass `--provider openai` explicitly:

```bash
uv run pico --provider openai
```

By default, the OpenAI-compatible endpoint points at right.codes' Codex endpoint:

```bash
PICO_OPENAI_API_BASE="https://www.right.codes/codex/v1"
PICO_RIGHT_CODES_API_KEY="your-right-codes-key"
PICO_OPENAI_MODEL="gpt-5.4"
```

You can also point it at a different OpenAI-compatible service:

```bash
PICO_OPENAI_API_BASE="https://your-api.example/v1"
PICO_OPENAI_API_KEY="your-api-key"
PICO_OPENAI_MODEL="gpt-5.4"
```

### Anthropic-compatible endpoint

To switch to an Anthropic-compatible service, pass `--provider anthropic` explicitly:

```bash
uv run pico --provider anthropic
```

By default, the Anthropic-compatible endpoint points at right.codes' Claude endpoint:

```bash
PICO_ANTHROPIC_API_BASE="https://www.right.codes/claude/v1"
PICO_RIGHT_CODES_API_KEY="your-right-codes-key"
PICO_ANTHROPIC_MODEL="claude-sonnet-4-6"
```

If your backend shares one key across multiple compatible endpoints, `pico` also supports falling back from `PICO_ANTHROPIC_API_KEY` to `ANTHROPIC_API_KEY`, `PICO_RIGHT_CODES_API_KEY`, `RIGHT_CODES_API_KEY`, `PICO_OPENAI_API_KEY`, or `OPENAI_API_KEY`.

### Ollama

To switch to a local Ollama instance, pass `--provider ollama` explicitly:

```bash
ollama serve
ollama pull qwen3.5:4b
uv run pico --provider ollama --model qwen3.5:4b
```

## Common interactive commands

- `/help`: list built-in commands
- `/memory`: view distilled working memory
- `/session`: view the current session file path
- `/reset`: clear the current session state
- `/exit` or `/quit`: exit the REPL

## Safety and persistence

`pico` does not open up every action by default. High-risk operations — shell execution, file writes — are gated by an approval mode:

- `--approval ask`
- `--approval auto`
- `--approval never`

At the end of every run, these files are written under `.pico/runs/<run_id>/`:

- `task_state.json`
- `trace.jsonl`
- `report.json`

These are local-only by default and don't need to be committed alongside the repository.

## Development

Common local checks:

```bash
uv run pytest tests -q
uv run ruff check pico tests scripts
```

The internal code is now split along lighter boundaries: `pico/evaluation/` holds benchmarks and metrics, `pico/providers/` holds model provider clients, and `pico/features/` holds optional runtime capabilities. New code should import directly from these package paths; the legacy `pico.evaluator`, `pico.metrics`, `pico.models`, and `pico.memory` imports are no longer kept as public entry points.
