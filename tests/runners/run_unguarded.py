"""Unguarded runner — full tool set, no guardrails of any kind."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from agents import Runner
from src.agents.unguarded_agents import unguarded_triage_agent
from tests.helpers.trace import print_trace

console = Console()


async def run_unguarded(test_cases: list[dict], title: str, subtitle: str) -> None:
    console.print(Panel.fit(
        f"[bold red]{title}[/bold red]\n[dim]{subtitle}[/dim]",
        border_style="red",
    ))
    console.print()

    for i, case in enumerate(test_cases, 1):
        console.rule(f"[bold]Test {i}: {case['label']}[/bold]")
        console.print(f"[cyan]Input:[/cyan]     {case['input']}")
        if "watch_for" in case:
            console.print(f"[bold red]Watch for:[/bold red] {case['watch_for']}")
        console.print(f"[dim]{case['note']}[/dim]")
        console.print()

        try:
            result = await Runner.run(unguarded_triage_agent, input=case["input"])
            console.print("[yellow]⚠  NO GUARDRAILS — no safety net[/yellow]")
            print_trace(result)
            console.print(Panel(
                Text(result.final_output, style="white"),
                title=f"[yellow]{result.last_agent.name}[/yellow]",
                border_style="yellow",
            ))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

        console.print()

    console.print(Panel.fit(
        "[bold yellow]SUMMARY — What just happened[/bold yellow]\n\n"
        "No input was filtered. No output was validated.\n"
        "Off-topic and unsafe inputs went straight through.\n\n"
        "[bold]Now run the guarded version →[/bold]",
        border_style="yellow",
    ))
