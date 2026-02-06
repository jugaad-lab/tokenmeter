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

### 📊 Rich CLI Dashboard with Cache Tracking
```
╭─────────────────── tokenmeter ───────────────────╮
│  TODAY  $122.42  (396.9K tokens)                 │
│  WEEK  $1142.22  (3.4M tokens)                   │
╰──────────────────────────────────────────────────╯

Provider   Input   Output  Cache R  Cache W  Total    Cost
───────────────────────────────────────────────────────────
Anthropic  12.2K   384.7K  116.4M   13.1M    396.9K   $122.42
```

**Cache R** and **Cache W** show prompt caching usage:
- **Cache Write**: Tokens stored in cache (paid once, slightly more expensive)
- **Cache Read**: Tokens reused from cache (90% cheaper than regular input)

This reveals the true value of OpenClaw/Claude's prompt caching. In this example:
- 116.4M cache reads saved ~$350 vs sending as regular input
- Cache reads are the #1 cost saver for heavy users

### 🔄 Automatic Import
- Claude Code usage logs
- OpenAI API response headers
- Custom webhook endpoint for proxy integration

### 📈 Analytics
- Daily/weekly/monthly trends
- Cost by model breakdown
- Input vs output token ratios
- **Cache token tracking** (reads + writes)
- Peak usage hours

### 💾 Cache Token Tracking

tokenmeter tracks **prompt caching** usage from OpenClaw and Claude:

**What is prompt caching?**
- Instead of sending your entire context every turn, Claude stores it in cache
- You pay slightly more to WRITE to cache once
- Then pay 90% LESS to READ from cache on subsequent turns

**Real-world example:**
```
Without caching: 1 billion tokens × $3/M = $3,000
With caching: 1 billion tokens × $0.30/M = $300
Savings: $2,700
```

tokenmeter shows both cache reads and writes so you can see exactly how much you're saving.

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
