# 🪙 tokenmeter

**Track your AI API usage and costs across all providers — locally, privately.**

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## Why This Exists

You're using Claude Code, Cursor, ChatGPT, Azure OpenAI, and a dozen other AI tools. Your monthly bill is a mystery until it arrives. Sound familiar?

**tokenmeter** solves this by:
- 📊 Tracking token usage across OpenAI, Anthropic, Azure OpenAI, and Google
- 💰 Calculating real-time cost estimates based on current pricing
- 🔒 Running 100% locally — your data never leaves your machine
- 📈 Showing trends and breakdowns by model, day, and application

## Installation

```bash
pip install tokenmeter
# or
pipx install tokenmeter
```

## Quick Start

```bash
# Log a usage event manually
tokenmeter log --provider anthropic --model claude-sonnet-4 --input 1500 --output 500

# Import from Claude Code's usage file
tokenmeter import claude-code

# Show today's summary
tokenmeter summary

# Show cost breakdown
tokenmeter costs --period week

# Interactive dashboard
tokenmeter dashboard
```

## Features

### 🎯 Multi-Provider Support
- **Anthropic** (Claude 3.5, 4, Opus, Sonnet, Haiku)
- **OpenAI** (GPT-4, GPT-4o, o1, o3)
- **Azure OpenAI** (all deployed models)
- **Google** (Gemini Pro, Ultra, Flash)

### 📊 Rich CLI Dashboard
```
╭─────────────────── tokenmeter ───────────────────╮
│  Today's Usage                                   │
│  ──────────────────────────────────────────────  │
│  Provider     Tokens      Cost                   │
│  Anthropic    45,230      $0.68                  │
│  OpenAI       12,100      $0.24                  │
│  ──────────────────────────────────────────────  │
│  Total        57,330      $0.92                  │
╰──────────────────────────────────────────────────╯
```

### 🔄 Automatic Import
- Claude Code usage logs
- OpenAI API response headers
- Custom webhook endpoint for proxy integration

### 📈 Analytics
- Daily/weekly/monthly trends
- Cost by model breakdown
- Input vs output token ratios
- Peak usage hours

## Configuration

```bash
# Set up pricing (auto-fetched, but customizable)
tokenmeter config --show

# Set budget alerts
tokenmeter alert --daily 5.00 --weekly 25.00
```

## How It Works

1. **Manual logging**: Use `tokenmeter log` after API calls
2. **Proxy mode**: Run `tokenmeter proxy` to intercept and log all LLM traffic
3. **Import mode**: Pull from existing usage logs (Claude Code, etc.)

All data stored in `~/.tokenmeter/usage.db` (SQLite).

## Privacy

- **Zero telemetry** — nothing sent anywhere
- **Local storage only** — SQLite database on your machine
- **No API keys stored** — we only track usage, not credentials
- **Open source** — audit the code yourself

## Roadmap

- [ ] VS Code extension
- [ ] Prometheus metrics export
- [ ] Slack/Discord alerts
- [ ] Team usage aggregation (self-hosted)

## License

MIT — use it, fork it, improve it.

---

*Built during a 5 AM coding session because AI bills are getting out of hand.* 🌅
