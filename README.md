# Context Under Compression — Prototype 0.1

An editorial workbench for source → draft → review → adjudication → revision. Includes the recorded pilot and an optional Python API runner. A manual response is never represented as a live model call.

## Hosted workbench

- Open the recorded example to compare the guided draft with the revision.
- Use **New run** or **Use this brief**. Add source text for repeatable evidence; a URL alone requires a model with browsing.
- Save the brief, copy each stage prompt into a fresh model session, and paste the response back. Record the model and settings if known.
- Every saved output is a new record. Changing an upstream output marks later records as outdated. New human decisions mark an existing revision outdated.
- Record explicit human decisions in Adjudicate. They are passed to revision.
- Export JSON for reimport or API execution; export Markdown for an inspectable report.

Working runs are saved in this browser's local storage, not synchronized to Drive or another device. Export backups. Pasted responses are local until deliberately exported or included in a model prompt. The page never asks for an API key. Demo records preserve reported provenance and separate combined original adjudication/revision output without pretending they were two independent calls.

## Python API runner

Python 3.10+; standard library only. Download the source archive from Evidence & export. Export a working run containing captured source text. A URL alone is intentionally not fetched by the runner.

Set `ANTHROPIC_API_KEY` in the local environment and pass an exact model identifier available in the API account. Do not put keys in JSON, commits, browser fields, or shared prompts. Usage is billed separately by Anthropic. No credential or paid live call was available during prototype construction; the adapter was tested with simulated responses only.

```bash
python python/runner.py content-run.json --stage draft --dry-run
python python/runner.py content-run.json --model YOUR_MODEL_ID --output generated-run.json
```

Each stage uses a fresh Messages API request with the persistent brief, captured source, and required prior outputs. Records are saved atomically after each completed stage. There are no automatic retries that might create duplicate charges. An API timeout may still have been billed.

For human review between stages:

```bash
python python/runner.py content-run.json --stage draft --model YOUR_MODEL_ID --output draft-run.json
python python/runner.py draft-run.json --stage review --model YOUR_MODEL_ID --output review-run.json
```

Continue with adjudication, import the result into the UI, add human decisions, export, and run revision. Every invocation requires a new output filename; input and prior outputs are never overwritten. Failed later stages leave a checkpoint containing earlier results. Imported runs get a new run identity in the UI.

The runner uses Anthropic's Messages HTTP interface (`/v1/messages`, `anthropic-version: 2023-06-01`). Reference: https://docs.anthropic.com/en/api/messages . The model is deliberately not hardcoded. Live account compatibility remains unverified.

## Evidence checks

Word counts use whitespace-delimited tokens containing a letter or number. Hyphenated words count as one; bullet markers do not count. Recorded pilot counts: baseline 247, guided 227, revision 248. Review tables are not measured against the post's word range. Year matching is a string check, not a factual verification. No accuracy score is invented. The source and prior outputs are treated as untrusted evidence in prompts, but prompt injection cannot be ruled out by wording alone.

## Local checks

```bash
node --test tests/core.test.mjs
python -m unittest discover -s tests -p 'test_*.py'
```

This is a static application with a local Python runner, not a hosted autonomous API service. Browser/API live end-to-end testing and multi-source reliability evaluation remain future validation work. No commercial readiness or general performance claim is made.

## Local interface

Serve the static files with `python -m http.server 8000 --directory dist` and open `http://localhost:8000` locally. ES modules require HTTP rather than opening the HTML as a file. Two optional WebMCP tools expose read-only run inspection and stage navigation when supported by the browser. A supported WebMCP browser was not available for validation, so these are progressive enhancements; all actions have ordinary interface controls.
