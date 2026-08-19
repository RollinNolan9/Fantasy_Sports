# AGENTS.md

## Cursor Cloud specific instructions

This repo is a set of Python CLI scripts (no web server, no UI, no test suite, no
lint config). Standard commands live in `README.md`; run scripts with
`python3 <script>.py` (e.g. `python3 model.py 2026`). Non-obvious notes:

- **Dependencies** are installed system-wide via `pip install --break-system-packages -r requirements.txt` (the startup update script handles this). The stock Python has no `venv`/`ensurepip`, so a virtualenv is not used; just call `python3` directly.
- **A real run needs a `CFBD_API_KEY`.** `fetch.py` reads it from the `CFBD_API_KEY` env var or a `.env` file (`CFBD_API_KEY=<key>`) and exits if it's missing. Get a free key at collegefootballdata.com. The API returns HTTP 401 without one.
- **`data/` is gitignored and starts empty.** `fetch.py` downloads all CSVs into `data/`; `model.py`, `projections.py`, and `backtest.py` all read from `data/` and fail with `FileNotFoundError: data/...csv` if it hasn't been populated. Correct order: `python3 fetch.py` first, then the model/backtest scripts.
- **`fetch.py` is cached/incremental.** It skips any `data/*.csv` that already exists, so re-running only pulls missing years — safe and cheap to re-run.
- **`model.py` and `projections.py` overwrite `projections_2026.csv`**, which is a committed file. If you run them for year 2026, restore it afterward with `git checkout -- projections_2026.csv` unless you intend to update it.
- **Without an API key**, you can still verify the pipeline runs by generating a synthetic `data/` fixture matching the CSV schemas the scripts read, then running `projections.py` / `model.py` / `backtest.py` end-to-end.
