# Repository Guidelines

## Project Structure & Module Organization
- `bot.py` is the entry point; it builds the runtime and boots Flask alongside the Discord client.
- `ourdiscordbot/` hosts services: `runtime.py` wires dependencies, `http_app.py` guards secrets, `discord_client.py` sends embeds, and `settings.py` centralises configuration.
- `ourdiscordbot/jira_handler.py` routes payloads into `jira_events/`, where modules register classifiers and embed builders through `registry.py`.
- `jira_smart_templates/` stores reusable JSON fragments for message bodies; extend them when new fields repeat.
- `tests/` mirrors the runtime layout with pytest suites. Place new tests beside the feature they cover.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` creates an isolated environment.
- `pip install -r requirements.txt` installs Flask, discord.py, pytest, and tooling.
- `python bot.py` runs the webhook listener locally; check `http://localhost:8080/health` after startup.
- `python -m pytest` executes the full test suite; add `-k "<keyword>"` for focused runs.
- `python -m black .` formats the repository; use `python -m black --check .` in CI or pre-commit hooks.

## Coding Style & Naming Conventions
Target Python 3.10+, four-space indentation, and type hints on public functions. Modules, files, and directories use `snake_case`; classes stay lean by extracting helpers into `jira_events.common`. Prefer dependency injection via factories such as `build_runtime()` and avoid module-level singletons. Run Black with the 100-character limit and let it break lines instead of manual spacing.

## Testing Guidelines
Pytest lives in `tests/` with mirrors such as `tests/test_runtime.py` and `tests/jira_events/test_status_transition.py`. Name files `test_<feature>.py`, keep focused fixtures close to the tests, and promote shared ones into `conftest.py`. Cover new branches in classifiers and embed renderers—assert critical fields rather than entire payloads. Run `python -m pytest --maxfail=1 --disable-warnings` before opening a PR.

## Commit & Pull Request Guidelines
Commits follow `DCBOT-<ticket>-<type>: <summary>`, using Conventional Commit types (feat, fix, docs, test, etc.). Keep summaries imperative and under 50 characters, and record motivation plus test evidence in the body. Pull requests link the Jira ticket, outline behavioural changes, and list automated or manual checks. Add screenshots for embed tweaks and document new environment variables.

## Configuration Tips
Export `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID`, `JIRA_WEBHOOK_SECRET`, and optional `PORT` before running locally; never commit secrets. Reference `docs/JiraEventHandlingArchitecture.md` when adding Jira events so operators can update automation payloads in lockstep.
