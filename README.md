# Context Under Compression — Prototype 0.1

An editorial workbench for source → draft → review → adjudication → revision. The hosted Sites deployment contains a private recorded pilot; this public repository contains the reusable prototype source and Python API runner, without that private run's drafts or prompts.

## Hosted workbench

- Use **New run** to create a working experiment.
- Add captured source text for repeatable evidence; a URL alone requires a model with browsing.
- Save the brief, copy each stage prompt into a fresh model session, and paste the response back.
- Every saved output is a new record. Changing upstream output marks later records outdated.
- Record explicit human decisions in Adjudicate. They are passed to revision.
- Export JSON for reimport or export a readable Markdown report.

Working runs are saved in this browser's local storage, not synchronized to Drive or another device. Export backups. The page never asks for an API key.

## Python API runner

Python 3.10+; standard library only. Export a working run containing captured source text, then run:

```bash
python python/runner.py content-run.json --stage draft --dry-run
python python/runner.py content-run.json --model YOUR_MODEL_ID --output generated-run.json
```

Set ANTHROPIC_API_KEY in the local environment. Usage is billed separately by Anthropic. The runner uses the Messages API and saves each completed stage atomically. It never overwrites an input file and does not automatically retry failed requests.

For human review between stages, run each stage with a new output filename, then import the resulting JSON into the workbench to add decisions before revision. A URL alone is intentionally not fetched by the runner.

## Evidence checks

Word counts use whitespace-delimited tokens containing a letter or number. No accuracy score is invented. Source and prior outputs are treated as untrusted evidence in prompts; prompt injection cannot be ruled out by wording alone.

## Local checks

```bash
node --test tests/core.test.mjs
python -m unittest discover -s tests -p 'test_*.py'
```

Serve locally with `python -m http.server 8000 --directory dist`. ES modules require HTTP rather than opening the HTML as a file. Optional WebMCP tools expose run inspection and stage navigation when supported; ordinary interface controls remain available.