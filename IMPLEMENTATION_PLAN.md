# Custom Time Ranges Implementation Plan

## Status: In Progress (Foundation Complete)

### ✅ Completed (Commit: cd00fb0)
- Created `tokenmeter/time_utils.py` with parse_time_input() and resolve_time_range()
- Supports natural language: "9am", "yesterday", "last week"
- Supports ISO timestamps
- Supports relative times: "1h ago", "2d ago"

### 🚧 Remaining Work

#### 1. Update db.py Functions
Modify `get_summary()` and `get_model_breakdown()` to accept optional start/end parameters:

```python
def get_summary(
    period: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    provider: Optional[str] = None,
) -> dict:
    # If start/end provided, use them
    # Otherwise fall back to period-based logic (backward compat)
```

#### 2. Update CLI Commands
Add new options to `summary`, `costs`, and `history` commands:

```python
@app.command()
def summary(
    period: Optional[str] = typer.Option(None, "--period", "-p"),
    since: Optional[str] = typer.Option(None, "--since"),
    after: Optional[str] = typer.Option(None, "--after"),
    between: Optional[List[str]] = typer.Option(None, "--between"),
    provider: Optional[str] = typer.Option(None, "--provider"),
):
    from .time_utils import resolve_time_range
    start, end = resolve_time_range(period=period, since=since, after=after, between=tuple(between) if between else None)
    # Pass start/end to get_summary()
```

#### 3. Add Tests
- Test time parsing edge cases
- Test backward compatibility with --period
- Test custom ranges

#### 4. Update Documentation
- Add examples to README.md
- Update SKILL.md with new CLI flags

### Example Usage (Post-Implementation)
```bash
token meter summary --since "9am"
tokenmeter costs --after "2026-02-06 09:00"
tokenmeter summary --between "9am" "5pm"
tokenmeter history --since "yesterday"
```

### Related Issues
- Fixes #3 (custom time ranges)
