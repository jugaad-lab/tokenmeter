<p align="center">
  <img src="assets/logo.png" alt="tokenmeter logo" width="200" />
</p>

[![ClawHub](https://img.shields.io/badge/ClawHub-tokenmeter-teal)](https://clawhub.ai/skills/tokenmeter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Repo stars](https://img.shields.io/github/stars/jugaad-lab/tokenmeter?style=social)](https://github.com/jugaad-lab/tokenmeter/stargazers)

**Install via ClawHub:** `clawhub install tokenmeter`

# 🪙 tokenmeter

> ⭐ **Found this useful? [Star this repo](https://github.com/jugaad-lab/tokenmeter)** to help others discover it!

**Track your AI API usage and costs across all providers — locally, privately.**

> 📌 **If you find this useful, please ⭐ star this repo!** It helps other developers discover cost tracking tools.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)

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

### Database Schema

Each usage record contains:

| Field | Description |
|-------|-------------|
| `timestamp` | When the API call happened |
| **`provider`** | **API provider** (anthropic, openai, google, azure) |
| `model` | Model name (claude-opus-4, gpt-4o, etc.) |
| **`app`** | **Session/workspace label** (clawdbot, claude-code, openclaw) |
| `input_tokens` | Input tokens consumed |
| `output_tokens` | Output tokens generated |
| `cache_read_tokens` | Tokens read from cache |
| `cache_write_tokens` | Tokens written to cache |
| `cost` | Calculated cost in USD |
| `source` | How this was logged (import, manual, proxy) |

#### Understanding `app` vs `provider`

- **`provider`**: The actual API provider (who you're paying)
  - Example: `anthropic` when using Claude via API
  - Example: `openai` when using GPT-4
  
- **`app`**: The tool/session that made the request (for organizational purposes)
  - Example: `clawdbot` - requests from your OpenClaw bot
  - Example: `claude-code` - requests from Claude Code CLI
  - Example: Custom label you set with `--app` flag

**Common confusion:** After migrating from "Clawdbot" to "OpenClaw", you may see sessions labeled `app=clawdbot` but with `provider=anthropic`. This is correct — the `app` label persists from the original session name, while `provider` shows who's actually billing you.

**Note:** `.openclaw` and `.clawdbot` directories may point to the same data (symlink). Both are imported as `app=clawdbot` for historical sessions.

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

## 🤝 Contributing

Found a bug? Have an idea? [Open an issue](https://github.com/jugaad-lab/tokenmeter/issues) or submit a PR!

If this tool saved you time, please ⭐ **star this repo** — it helps others find it.

## License

MIT — use it, fork it, improve it.

---
## More from Jugaad Lab 🔧
| Tool | What it does |
|------|-------------|
| [claude-code-mastery](https://github.com/jugaad-lab/claude-code-mastery) | Master Claude Code with subagents & automation |
| [tokenmeter](https://github.com/jugaad-lab/tokenmeter) | Track AI token usage & costs locally |
| [clawguard](https://github.com/jugaad-lab/clawguard) | Security blacklist for AI agents |
| [clawdscan](https://github.com/jugaad-lab/clawdscan) | Session health analyzer for OpenClaw |
| [skilldoc](https://github.com/jugaad-lab/skilldoc) | Skill health checker for OpenClaw |
| [tribe-protocol](https://github.com/jugaad-lab/tribe-protocol) | Trust & access control for AI bots |
| [discord-voice-plugin](https://github.com/jugaad-lab/discord-voice-plugin) | Voice conversations with AI in Discord |
| [worldmonitor](https://github.com/jugaad-lab/worldmonitor) | Real-time global intelligence dashboard |

⭐ **Found these useful? Star the repos you like!**

---

*Built during a 5 AM coding session because AI bills are getting out of hand.* 🌅
