# tokenmeter - AI Usage & Cost Tracking for OpenClaw

Track your AI token usage and costs across all providers — locally, privately.

## Overview

**tokenmeter** is a CLI tool that tracks LLM API usage and calculates real-time cost estimates. For OpenClaw users on the Claude Max plan, it helps:

1. **Prove Max plan value** - Show what you *would* have paid on API billing
2. **Monitor usage patterns** - Understand which models you use most
3. **Catch overages early** - Know if you're using expensive models too much
4. **Unified tracking** - Track usage across multiple OpenClaw instances

All data stays local (SQLite at `~/.tokenmeter/usage.db`). No telemetry, no cloud sync.

---

## Installation

**For bot/agent (admin runs once):**

```bash
cd ~/clawd
git clone https://github.com/jugaad-lab/tokenmeter.git
```

The repo contains:
- Python package (tokenmeter CLI)
- Documentation (this file is in `docs/openclaw-skill/`)
- Example scripts

**First-time setup (bot does this automatically when needed):**

```bash
cd ~/clawd/tokenmeter

# Setup venv if it doesn't exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e .
fi
```

**After first setup:** Bot just activates venv and runs commands.

---

## Usage (Bot Commands)

**Standard pattern for all tokenmeter commands:**

```bash
cd ~/clawd/tokenmeter && source .venv/bin/activate && tokenmeter [command]
```

**Examples:**
```bash
# Import latest usage
cd ~/clawd/tokenmeter && source .venv/bin/activate && tokenmeter import --auto

# Quick overview
cd ~/clawd/tokenmeter && source .venv/bin/activate && tokenmeter dashboard

# Weekly breakdown
cd ~/clawd/tokenmeter && source .venv/bin/activate && tokenmeter costs --period week
```

**Tip:** Bot can create an alias for shorter commands:
```bash
alias tm='cd ~/clawd/tokenmeter && source .venv/bin/activate && tokenmeter'
# Then just: tm dashboard
```

---

## Usage

### Quick Commands

```bash
# Discover session sources (OpenClaw, Claude Code, etc.)
tokenmeter scan

# Import all discovered sessions
tokenmeter import --auto

# Preview import without writing
tokenmeter import --auto --dry-run

# Show today's usage
tokenmeter dashboard

# Weekly summary
tokenmeter summary --period week

# Cost breakdown by model
tokenmeter costs --period month

# List all supported models + pricing
tokenmeter models

# View recent history
tokenmeter history --limit 20
```

---

## Integration with OpenClaw

### Automatic Import (Recommended)

OpenClaw writes token usage to session JSONL files at:
```
~/.clawdbot/agents/*/sessions/*.jsonl
```

**Step 1: Discover session sources**

```bash
cd ~/clawd/tokenmeter
source .venv/bin/activate
tokenmeter scan
```

This shows all discovered session directories:
- `.clawdbot/agents/main/sessions/` (OpenClaw)
- `.claude/projects/*/sessions/` (Claude Code)
- Any other compatible session formats

**Step 2: Import all at once**

```bash
tokenmeter import --auto
```

This will:
- Parse all discovered session files
- Extract token usage from each LLM call
- Log to tokenmeter with API-equivalent costs
- Skip already-imported entries (idempotent)
- Show total records and cost

**Options:**
```bash
tokenmeter import --auto --dry-run  # Preview without writing
tokenmeter import --path ~/.clawdbot/agents/main/sessions/  # Import specific directory
```

**Recommended:** Run `tokenmeter import --auto` daily via cron or manually after heavy usage.

### Manual Logging (Fallback)

If you need to log usage manually:

```bash
tokenmeter log \
  --provider anthropic \
  --model claude-sonnet-4 \
  --input 1500 \
  --output 500 \
  --app openclaw
```

Options:
- `--provider` / `-p`: anthropic, openai, google, azure
- `--model` / `-m`: Model name (see `tokenmeter models`)
- `--input` / `-i`: Input tokens
- `--output` / `-o`: Output tokens
- `--app` / `-a`: Application name (e.g., "openclaw")

---

## Understanding the Data

### Model Pricing (as of Feb 2026)

| Token Type | claude-sonnet-4 | claude-opus-4 | claude-3.5-haiku |
|------------|----------------|---------------|------------------|
| **Input** | $3.00/1M | $15.00/1M | $0.80/1M |
| **Output** | $15.00/1M | $75.00/1M | $4.00/1M |
| **Cache Write** | $3.75/1M | $18.75/1M | $1.00/1M |
| **Cache Read** | $0.30/1M | $1.50/1M | $0.08/1M |

### Understanding Cache Tokens

**What are cache tokens?**

OpenClaw (and Claude) use **prompt caching** to store parts of your conversation in memory. This means you don't send the same context repeatedly.

**Two types of cache tokens:**

1. **Cache WRITE tokens** - Tokens sent ONCE and stored in cache
   - Example: Your entire codebase, documentation, system prompts
   - Slightly more expensive than regular input (~25% markup)
   - Only paid once, then reused for free (almost)

2. **Cache READ tokens** - Tokens reused from cache
   - You're NOT sending these again - Claude reads them from memory
   - **90% cheaper** than regular input tokens
   - This is where massive savings come from

**Real example from our usage:**
```
This Month:
Regular Input:    119.5K tokens  ($0.36)
Regular Output:     3.8M tokens  ($57.00)
Cache Write:      157.2M tokens  ($589.50 - paid once)
Cache Read:     1,024.3M tokens  ($307.29 - 90% discount!)
Total: $954.15
```

Without caching, we'd send ~1.2 BILLION tokens as regular input ($3,600+).
With caching: We only pay $307 for those cache reads.

**Savings: $3,293** from caching alone this month! 🎉

### Reading the Dashboard

```
╭─────────────────── tokenmeter ───────────────────╮
│  TODAY  $122.42  (396.9K tokens)                 │
│  WEEK  $1142.22  (3.4M tokens)                   │
╰──────────────────────────────────────────────────╯

Provider   Input   Output  Cache R  Cache W  Total    Cost
───────────────────────────────────────────────────────────
Anthropic  12.2K   384.7K  116.4M   13.1M    396.9K   $122.42
```

**Reading the columns:**
- **Input**: Fresh tokens sent to Claude
- **Output**: Tokens Claude generated
- **Cache R**: Tokens reused from cache (READ)
- **Cache W**: Tokens written to cache (WRITE)
- **Total**: Input + Output (regular tokens only)
- **Cost**: API-equivalent cost

**Why Cache R is so large:** Every time you continue a conversation, Claude reads your entire context from cache instead of you sending it fresh. Over many turns, this adds up to billions of tokens reused.

**Cost breakdown:**
- Regular tokens: Expensive ($3-15 per 1M)
- Cache Write: Slightly more expensive (~25% markup)
- Cache Read: **90% cheaper** ($0.30-1.50 per 1M)

This is why the cost stays low despite huge cache numbers.

### Comparing to Claude Max Plan

**Your Max plan:** $100/month flat rate

**If tokenmeter shows $800 this month:**
- API-equivalent cost: $800
- Max plan cost: $100
- **Savings: $700** ✅

**If tokenmeter shows $90 this month:**
- API-equivalent cost: $90
- Max plan cost: $100
- **Overpaying by $10** (but you get peace of mind!)

---

## Workflows

### Daily Check-In

```bash
cd ~/clawd/tokenmeter
source .venv/bin/activate

# Import latest usage
tokenmeter import --auto

# Quick overview
tokenmeter dashboard
```

### Weekly Review

```bash
tokenmeter summary --period week
tokenmeter costs --period week
```

Look for:
- Heavy Opus usage (expensive!)
- Unusual spikes
- High output token counts (code generation, long responses)

### Monthly Billing Comparison

At month end:

```bash
tokenmeter costs --period month
```

Compare to your Anthropic invoice:
- Max plan: $100 flat
- API-equivalent (tokenmeter): $XXX
- Delta = savings (or loss)

---

## Cron Automation (Optional)

Add to your HEARTBEAT.md or run via cron:

```bash
# Run daily at 11 PM
0 23 * * * cd ~/clawd/tokenmeter && source .venv/bin/activate && tokenmeter import --auto
```

This keeps tokenmeter in sync without manual effort.

---

## Multi-Bot Tracking

If you run multiple OpenClaw instances (e.g., Cheenu + Chhotu):

1. Both bots import to tokenmeter on their respective machines
2. Each uses `--app` flag to distinguish:
   ```bash
   tokenmeter log -p anthropic -m claude-sonnet-4 -i 1000 -o 500 --app cheenu
   tokenmeter log -p anthropic -m claude-sonnet-4 -i 800 -o 400 --app chhotu
   ```
3. Nagaconda can aggregate reports from both to see total team usage

---

## Troubleshooting

### "tokenmeter: command not found"

Activate the virtual environment:
```bash
cd ~/clawd/skills/tokenmeter
source .venv/bin/activate
```

### Empty dashboard after import

Check:
1. OpenClaw session files exist: `ls ~/.clawdbot/agents/*/sessions/*.jsonl`
2. Import command ran successfully (no errors)
3. Database has entries: `sqlite3 ~/.tokenmeter/usage.db "SELECT COUNT(*) FROM usage;"`

### Prices seem wrong

Pricing is based on API rates as of Feb 2026. If Anthropic changes pricing, update `tokenmeter/pricing.py` or open an issue on GitHub.

---

## Examples

### Example 1: Check today's usage

```bash
$ tokenmeter dashboard
╭─────────────────── tokenmeter ───────────────────╮
│  TODAY  $4.23  (141,000 tokens)                  │
│  WEEK   $28.90  (963,000 tokens)                 │
╰──────────────────────────────────────────────────╯
```

**Analysis:** $4.23 today, trending toward ~$30/week. Well within Max plan ($100/mo).

### Example 2: Weekly cost breakdown

```bash
$ tokenmeter costs --period week

Provider   Model              Input      Output     Cost      %
─────────────────────────────────────────────────────────────
Anthropic  claude-sonnet-4    450K       180K       $4.05    45%
Anthropic  claude-opus-4       90K        30K       $3.60    40%
Anthropic  claude-3.5-haiku   800K       200K       $1.44    15%
─────────────────────────────────────────────────────────────
Total                        1,340K      410K       $9.09   100%
```

**Analysis:** Using Opus for 40% of costs but only ~7% of token volume. Consider using Sonnet more.

### Example 3: Month-end comparison (Real Data - Feb 2026)

```bash
$ tokenmeter import --auto
Imported 13,713 records
Total cost: $1,246.55

$ tokenmeter costs --period month

Model                    Input   Output    Cost      % of Total
─────────────────────────────────────────────────────────────────
anthropic/claude-opus-4  47.3K   1.6M      $743.35   59.6%
anthropic/claude-sonnet-4 70.8K  2.2M      $501.75   40.3%
─────────────────────────────────────────────────────────────────
Total                    118.8K  3.8M      $1,246.55 100%

$ tokenmeter summary --period month

Provider   Input    Output   Total    Cost        Requests
─────────────────────────────────────────────────────────
Anthropic  118.8K   3.8M     3.9M     $1,246.55   12,552
```

**Analysis:** 
- API-equivalent cost: **$1,246.55**
- Max plan cost: **$100.00**
- **Savings: $1,146.55** ✅

Opus usage (59.6% of cost) shows heavy extended-thinking use. Max plan absolutely paid for itself this month!

---

## FAQ

**Q: Does tokenmeter send data anywhere?**
A: No. Everything is stored locally in `~/.tokenmeter/usage.db`. Zero telemetry.

**Q: What if I delete the database?**
A: You lose history, but can rebuild by re-importing OpenClaw sessions (idempotent).

**Q: Can I use this with non-OpenClaw tools?**
A: Yes! It supports Claude Code, Cursor, and manual logging for any LLM tool.

**Q: Will this slow down OpenClaw?**
A: No. Import runs separately and reads logs after-the-fact.

**Q: What about cache tokens?**
A: tokenmeter includes cache read/write tokens in its calculations (OpenClaw tracks them).

---

## References

- **GitHub:** https://github.com/jugaad-lab/tokenmeter
- **OpenClaw Docs:** https://docs.openclaw.ai
- **Anthropic Pricing:** https://anthropic.com/pricing

---

## Changelog

### 2026-02-06 (v2)
- ✅ `tokenmeter scan` - Auto-discover session sources
- ✅ `tokenmeter import --auto` - Import all discovered sessions
- ✅ Real data example showing $1,146 monthly savings on Max plan
- ✅ Updated workflows with new commands
- ✅ Tested on actual OpenClaw + Claude Code sessions

### 2026-02-06 (v1)
- Initial skill creation
- Documented installation and usage
- Added workflow examples

---

*Built to answer the question: "How much is my Max plan really saving me?" 💰*
