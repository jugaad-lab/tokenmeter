"""SQLite database for storing usage data."""

import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class UsageRecord:
    """A single usage record."""
    id: Optional[int]
    timestamp: datetime
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    source: str  # 'manual', 'import', 'proxy'
    app: Optional[str]  # Application name (e.g., 'claude-code', 'cursor')


DB_PATH = Path.home() / ".tokenmeter" / "usage.db"


def get_db_path() -> Path:
    """Get the database path, creating directory if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DB_PATH


def init_db() -> sqlite3.Connection:
    """Initialize the database and return connection."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            cost REAL NOT NULL,
            source TEXT NOT NULL DEFAULT 'manual',
            app TEXT
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage(timestamp)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_usage_provider ON usage(provider)
    """)
    
    conn.commit()
    return conn


def log_usage(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost: float,
    source: str = "manual",
    app: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> int:
    """Log a usage record and return the ID."""
    conn = init_db()
    ts = timestamp or datetime.now()
    
    cursor = conn.execute(
        """
        INSERT INTO usage (timestamp, provider, model, input_tokens, output_tokens, cost, source, app)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (ts.isoformat(), provider, model, input_tokens, output_tokens, cost, source, app)
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id


def get_usage(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> list[UsageRecord]:
    """Query usage records with optional filters."""
    conn = init_db()
    
    query = "SELECT * FROM usage WHERE 1=1"
    params = []
    
    if start:
        query += " AND timestamp >= ?"
        params.append(start.isoformat())
    if end:
        query += " AND timestamp <= ?"
        params.append(end.isoformat())
    if provider:
        query += " AND provider = ?"
        params.append(provider)
    if model:
        query += " AND model = ?"
        params.append(model)
    
    query += " ORDER BY timestamp DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    return [
        UsageRecord(
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            provider=row["provider"],
            model=row["model"],
            input_tokens=row["input_tokens"],
            output_tokens=row["output_tokens"],
            cost=row["cost"],
            source=row["source"],
            app=row["app"],
        )
        for row in rows
    ]


def get_summary(
    period: str = "day",
    provider: Optional[str] = None,
) -> dict:
    """Get aggregated summary for a time period."""
    now = datetime.now()
    
    if period == "day":
        start = datetime.combine(date.today(), datetime.min.time())
    elif period == "week":
        start = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    elif period == "month":
        start = datetime.combine(date.today() - timedelta(days=30), datetime.min.time())
    else:
        start = None
    
    records = get_usage(start=start, provider=provider)
    
    # Aggregate by provider
    by_provider = {}
    for r in records:
        if r.provider not in by_provider:
            by_provider[r.provider] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost": 0.0,
                "requests": 0,
            }
        by_provider[r.provider]["input_tokens"] += r.input_tokens
        by_provider[r.provider]["output_tokens"] += r.output_tokens
        by_provider[r.provider]["total_tokens"] += r.input_tokens + r.output_tokens
        by_provider[r.provider]["cost"] += r.cost
        by_provider[r.provider]["requests"] += 1
    
    # Totals
    total_input = sum(r.input_tokens for r in records)
    total_output = sum(r.output_tokens for r in records)
    total_cost = sum(r.cost for r in records)
    
    return {
        "period": period,
        "start": start.isoformat() if start else None,
        "end": now.isoformat(),
        "by_provider": by_provider,
        "totals": {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "cost": total_cost,
            "requests": len(records),
        }
    }


def get_model_breakdown(period: str = "day") -> dict:
    """Get usage breakdown by model."""
    now = datetime.now()
    
    if period == "day":
        start = datetime.combine(date.today(), datetime.min.time())
    elif period == "week":
        start = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    elif period == "month":
        start = datetime.combine(date.today() - timedelta(days=30), datetime.min.time())
    else:
        start = None
    
    records = get_usage(start=start)
    
    # Aggregate by model
    by_model = {}
    for r in records:
        key = f"{r.provider}/{r.model}"
        if key not in by_model:
            by_model[key] = {
                "provider": r.provider,
                "model": r.model,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
                "requests": 0,
            }
        by_model[key]["input_tokens"] += r.input_tokens
        by_model[key]["output_tokens"] += r.output_tokens
        by_model[key]["cost"] += r.cost
        by_model[key]["requests"] += 1
    
    return {
        "period": period,
        "models": list(by_model.values()),
    }
