"""CLI interface for tokenmeter."""

import typer
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from . import __version__
from .pricing import calculate_cost, get_pricing, list_supported_models
from .db import log_usage, get_summary, get_model_breakdown, get_usage

app = typer.Typer(
    name="tokenmeter",
    help="Track your AI API usage and costs across all providers — locally, privately.",
    no_args_is_help=True,
)
console = Console()


def format_tokens(n: int) -> str:
    """Format token count with K/M suffixes."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def format_cost(cost: float) -> str:
    """Format cost in dollars."""
    if cost < 0.01:
        return f"${cost:.4f}"
    return f"${cost:.2f}"


@app.command()
def log(
    provider: str = typer.Option(..., "--provider", "-p", help="Provider (anthropic, openai, google, azure)"),
    model: str = typer.Option(..., "--model", "-m", help="Model name"),
    input_tokens: int = typer.Option(..., "--input", "-i", help="Input tokens"),
    output_tokens: int = typer.Option(..., "--output", "-o", help="Output tokens"),
    app_name: Optional[str] = typer.Option(None, "--app", "-a", help="Application name"),
):
    """Log a usage event manually."""
    cost = calculate_cost(provider, model, input_tokens, output_tokens)
    
    pricing = get_pricing(provider, model)
    if not pricing:
        console.print(f"[yellow]⚠️  Unknown model {provider}/{model} - cost set to $0[/yellow]")
    
    record_id = log_usage(
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        source="manual",
        app=app_name,
    )
    
    console.print(f"[green]✓[/green] Logged usage #{record_id}")
    console.print(f"  Provider: {provider}")
    console.print(f"  Model: {model}")
    console.print(f"  Tokens: {format_tokens(input_tokens)} in / {format_tokens(output_tokens)} out")
    console.print(f"  Cost: [bold]{format_cost(cost)}[/bold]")


@app.command()
def summary(
    period: str = typer.Option("day", "--period", "-p", help="Time period (day, week, month)"),
    provider: Optional[str] = typer.Option(None, "--provider", help="Filter by provider"),
):
    """Show usage summary."""
    console.print()
    data = _render_summary_table(period=period, provider=provider)
    
    if data["totals"]["requests"] == 0:
        console.print("\n[dim]No usage recorded for this period. Use 'tokenmeter log' to add records.[/dim]")
    console.print()


@app.command()
def costs(
    period: str = typer.Option("day", "--period", "-p", help="Time period (day, week, month)"),
):
    """Show cost breakdown by model."""
    data = get_model_breakdown(period=period)
    
    period_label = {"day": "Today", "week": "This Week", "month": "This Month"}.get(period, period)
    
    table = Table(
        title=f"💰 Cost Breakdown — {period_label}",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Model", style="bold")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Cost", justify="right", style="green")
    table.add_column("% of Total", justify="right")
    
    total_cost = sum(m["cost"] for m in data["models"])
    
    # Sort by cost descending
    for model in sorted(data["models"], key=lambda x: x["cost"], reverse=True):
        pct = (model["cost"] / total_cost * 100) if total_cost > 0 else 0
        table.add_row(
            f"{model['provider']}/{model['model']}",
            format_tokens(model["input_tokens"]),
            format_tokens(model["output_tokens"]),
            format_cost(model["cost"]),
            f"{pct:.1f}%",
        )
    
    console.print()
    console.print(table)
    
    if not data["models"]:
        console.print("\n[dim]No usage recorded. Use 'tokenmeter log' to add records.[/dim]")
    console.print()


@app.command()
def models():
    """List supported models and their pricing."""
    table = Table(
        title="📋 Supported Models & Pricing",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Provider", style="bold")
    table.add_column("Model")
    table.add_column("Input ($/1M)", justify="right", style="yellow")
    table.add_column("Output ($/1M)", justify="right", style="green")
    
    current_provider = None
    for provider, model in list_supported_models():
        pricing = get_pricing(provider, model)
        if pricing:
            # Add section between providers
            if current_provider and provider != current_provider:
                table.add_section()
            current_provider = provider
            
            table.add_row(
                provider.capitalize(),
                pricing.model,
                f"${pricing.input_per_1m:.2f}",
                f"${pricing.output_per_1m:.2f}",
            )
    
    console.print()
    console.print(table)
    console.print()


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of records to show"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
):
    """Show recent usage history."""
    records = get_usage(provider=provider)[:limit]
    
    table = Table(
        title="📜 Recent Usage",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Time", style="dim")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Tokens", justify="right")
    table.add_column("Cost", justify="right", style="green")
    table.add_column("Source", style="dim")
    
    for r in records:
        table.add_row(
            r.timestamp.strftime("%m/%d %H:%M"),
            r.provider,
            r.model,
            f"{format_tokens(r.input_tokens)}/{format_tokens(r.output_tokens)}",
            format_cost(r.cost),
            r.source,
        )
    
    console.print()
    console.print(table)
    
    if not records:
        console.print("\n[dim]No usage history. Use 'tokenmeter log' to add records.[/dim]")
    console.print()


def _render_summary_table(period: str = "day", provider: Optional[str] = None):
    """Render summary table (internal helper)."""
    data = get_summary(period=period, provider=provider)
    
    period_label = {"day": "Today", "week": "This Week", "month": "This Month"}.get(period, period)
    
    table = Table(
        title=f"🪙 tokenmeter — {period_label}",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Provider", style="bold")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Cost", justify="right", style="green")
    table.add_column("Requests", justify="right")
    
    for prov, stats in sorted(data["by_provider"].items()):
        table.add_row(
            prov.capitalize(),
            format_tokens(stats["input_tokens"]),
            format_tokens(stats["output_tokens"]),
            format_tokens(stats["total_tokens"]),
            format_cost(stats["cost"]),
            str(stats["requests"]),
        )
    
    totals = data["totals"]
    if totals["requests"] > 0:
        table.add_section()
        table.add_row(
            "[bold]TOTAL[/bold]",
            format_tokens(totals["input_tokens"]),
            format_tokens(totals["output_tokens"]),
            format_tokens(totals["total_tokens"]),
            f"[bold green]{format_cost(totals['cost'])}[/bold green]",
            str(totals["requests"]),
        )
    
    console.print(table)
    return data


@app.command()
def dashboard():
    """Show interactive dashboard (summary + costs + recent)."""
    console.print()
    
    # Today's summary
    today = get_summary(period="day")
    week = get_summary(period="week")
    
    # Quick stats panel
    stats_text = Text()
    stats_text.append("TODAY  ", style="bold cyan")
    stats_text.append(f"{format_cost(today['totals']['cost'])}  ", style="bold green")
    stats_text.append(f"({format_tokens(today['totals']['total_tokens'])} tokens)\n", style="dim")
    stats_text.append("WEEK   ", style="bold cyan")
    stats_text.append(f"{format_cost(week['totals']['cost'])}  ", style="bold green")
    stats_text.append(f"({format_tokens(week['totals']['total_tokens'])} tokens)", style="dim")
    
    console.print(Panel(
        stats_text,
        title="🪙 tokenmeter",
        border_style="cyan",
        padding=(1, 2),
    ))
    
    # Provider breakdown
    if today["totals"]["requests"] > 0:
        console.print()
        _render_summary_table(period="day")
    
    # Recent activity
    recent = get_usage()[:5]
    if recent:
        console.print("\n[bold]Recent Activity[/bold]")
        for r in recent:
            console.print(
                f"  [dim]{r.timestamp.strftime('%H:%M')}[/dim] "
                f"{r.provider}/{r.model} — "
                f"[green]{format_cost(r.cost)}[/green]"
            )
    
    console.print()


@app.command()
def version():
    """Show version information."""
    console.print(f"tokenmeter v{__version__}")


@app.callback()
def main():
    """
    🪙 tokenmeter - Track your AI API usage and costs
    
    All data is stored locally in ~/.tokenmeter/usage.db
    """
    pass


if __name__ == "__main__":
    app()
