# Claude Code Runtime Adapter

Read `SKILL.md` in full before using this project. Choose screenshot, PandaData, or hybrid mode from the user's evidence. Use the existing programs under `scripts/` instead of duplicating calculations.

## Data and safety

- PandaData is the only structured market-data source.
- In a Claude session, use the authorized PandaData MCP; pass only redacted structured rows to local scripts.
- Local SDK credentials may be read only at runtime from `PANDA_USERNAME` / `PANDA_PASSWORD` or `~/.pandadata/pandadata.env`.
- Never expose, persist, log, or commit accounts, passwords, tokens, cookies, or authorization headers.
- Do not use later data to confirm an earlier pattern, fill missing bars, cross the A-share lunch break, or treat an unclosed final bar as closed.
- Do not place orders, modify accounts, backtest, optimize strategies, promise returns, or provide direct trading instructions.

## Workflow

1. Read `SKILL.md` and the relevant files under `references/`.
2. Validate raw OHLCV with `scripts/ohlcv_validate.py`.
3. Resample with `scripts/resample_kline.py` for `1m/5m/10m/15m/30m/60m`.
4. Calculate only supported indicators with `scripts/indicators.py`.
5. Detect conservative candidates with `scripts/pattern_detection.py`.
6. Generate the chart and structured outputs with `scripts/analyze_kline.py`.
7. Report facts, interpretations, confirmation, invalidation, uncertainty, and data gaps separately.
