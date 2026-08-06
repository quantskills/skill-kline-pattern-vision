# K-line Pattern Vision

[简体中文](README.md) | English

> This is a QuantSkills community project maintained by GitHub user `cikeqi`. It has not been independently reviewed, is not officially endorsed by QuantSkills, and makes no promise of returns or production suitability.

A read-only K-line analysis skill with three modes:

1. **Screenshot mode**: analyze only a user-provided chart image.
2. **PandaData mode**: fetch and validate PandaData OHLCV, resample intraday data, calculate indicators, and generate a chart.
3. **Hybrid mode**: compare screenshot observations with structured PandaData facts.

> This is a research and educational tool. It is not investment advice, does not promise returns, and cannot place trades.

## Project layout

```text
skill-kline-pattern-vision/
├── SKILL.md
├── README.md / README.en.md
├── CLAUDE.md
├── LICENSE
├── requirements.txt
├── agents/
├── references/
├── scripts/
└── tests/
```

The scripts provide runtime authentication, OHLCV validation, intraday resampling, indicators, conservative pattern candidates, chart generation, and a one-shot CLI.

## Supported frequencies

- Daily: `1d`
- Intraday: `1m`, `5m`, `10m`, `15m`, `30m`, `60m`

Intraday bars are grouped separately for the morning and afternoon A-share sessions. Lunch breaks are never crossed, data is never interpolated, and an incomplete final bar is marked `complete: false`.

## Quick start

A Claude host may call the authorized PandaData MCP and pass a redacted dataframe JSON to the local pipeline:

```bash
python3 scripts/analyze_kline.py \
  --input /path/to/pandadata_dataframe.json \
  --frequency 10m \
  --out /tmp/kline-analysis
```

Outputs include `analysis.json`, `bars.json`, and `kline_10m.png`.

For local SDK use, install requirements. Credentials are read only at runtime from environment variables or `~/.pandadata/pandadata.env`; they must never be committed or pasted into source files.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Credential safety

The project must not contain real accounts, passwords, tokens, cookies, or authorization headers. Error messages and generated outputs must be sanitized. Do not ask users to paste secrets into chat.

## Testing

```bash
python3 -m pytest -q
```

Tests cover OHLCV validation, duplicate and ordering errors, intraday aggregation and lunch breaks, indicators, HH/HL/LH/LL structure, pattern candidates, and redacted JSON input.

## Analysis boundaries

HH means a higher high, HL a higher low, LH a lower high, and LL a lower low. Candlestick and chart patterns remain candidates until their confirmation conditions are met. Every candidate should state evidence, confirmation, invalidation, alternative explanations, and confidence. The skill does not calculate unsupported win rates or issue direct trading instructions.

Only approved PandaData data and user-provided screenshots may be used. Web data, broker APIs, undeclared caches, synthetic bars, and substitute data sources are prohibited.
