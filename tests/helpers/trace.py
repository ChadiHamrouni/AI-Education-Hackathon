"""Shared trace helpers for printing agent routing and tool calls."""

from rich.console import Console
from agents.items import ToolCallItem, ToolCallOutputItem

console = Console()


def _tool_name(raw_item) -> str:
    if hasattr(raw_item, "name"):
        return raw_item.name
    if isinstance(raw_item, dict):
        fn = raw_item.get("function", {})
        return fn.get("name", "?") if isinstance(fn, dict) else "?"
    fn = getattr(raw_item, "function", None)
    return getattr(fn, "name", "?") if fn else "?"


def _tool_args(raw_item) -> str:
    if hasattr(raw_item, "arguments"):
        return raw_item.arguments or ""
    if isinstance(raw_item, dict):
        fn = raw_item.get("function", {})
        return fn.get("arguments", "") if isinstance(fn, dict) else ""
    fn = getattr(raw_item, "function", None)
    return getattr(fn, "arguments", "") or "" if fn else ""


def print_trace(result) -> None:
    """Print agent routing, tool calls, and their results."""
    console.print(
        f"  [dim]Route:[/dim]  [dim]triage_agent[/dim] → [bold cyan]{result.last_agent.name}[/bold cyan]"
    )
    calls = [item for item in result.new_items if isinstance(item, ToolCallItem)]
    outputs = [item for item in result.new_items if isinstance(item, ToolCallOutputItem)]
    if calls:
        for i, call in enumerate(calls):
            name = _tool_name(call.raw_item)
            args = _tool_args(call.raw_item)
            result_str = str(outputs[i].output) if i < len(outputs) else "?"
            console.print(
                f"  [dim]Tool:[/dim]   [magenta]{name}[/magenta]({args})"
                f"  →  [yellow]{result_str}[/yellow]"
            )
    else:
        console.print(f"  [dim]Tools:[/dim]  [dim]none[/dim]")
    console.print()
