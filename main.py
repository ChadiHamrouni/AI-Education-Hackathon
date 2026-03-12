"""
Interactive Math Tutor — Full Guardrail Pipeline
================================================
Usage:
    python main.py   (from workshop/)
"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from agents import Runner, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from src.agents.triage_agent import triage_agent
from src.guardrails.output_guards import MathRunContext

console = Console()

EXAMPLES = [
    "What is 347 * 892?",
    "What is the derivative of x**3 + 2*x**2 - 5?",
    "Calculate the integral of sin(x)?",
    "What is 1024 / 32?",
    "What is the product rule?",
]

BANNER = """
╔══════════════════════════════════════════════════════════╗
║        AI-Powered Math Tutor  ·  Guardrails Workshop     ║
║   Powered by Qwen 3.5 4B  ·  OpenAI Agents SDK          ║
╚══════════════════════════════════════════════════════════╝
"""


async def chat(user_input: str) -> None:
    run_ctx = MathRunContext()
    try:
        result = await Runner.run(triage_agent, input=user_input, context=run_ctx)

        if run_ctx.was_tool_called:
            tools = [c["tool"] for c in run_ctx.tool_calls]
            console.print(f"[dim]Tools used: {tools}[/dim]")

        console.print(Panel(
            result.final_output,
            title=f"[green]{result.last_agent.name}[/green]",
            border_style="green",
        ))

    except InputGuardrailTripwireTriggered as e:
        info = e.guardrail_result.output.output_info
        name = e.guardrail_result.guardrail.name or "input guardrail"
        message = info.get("message", info.get("reason", "Request blocked."))
        console.print(Panel(
            f"[yellow]{message}[/yellow]",
            title=f"[yellow]🛡 {name}[/yellow]",
            border_style="yellow",
        ))

    except OutputGuardrailTripwireTriggered as e:
        info = e.guardrail_result.output.output_info
        name = e.guardrail_result.guardrail.name or "output guardrail"
        message = info.get("message", info.get("reason", "Response blocked."))
        console.print(Panel(
            f"[red]{message}[/red]",
            title=f"[red]🔴 {name}[/red]",
            border_style="red",
        ))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


async def main():
    console.print(BANNER, style="bold cyan")
    console.print("Type [bold]help[/bold] for examples, [bold]exit[/bold] to quit.\n")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break
        if user_input.lower() == "help":
            console.print("\n[bold]Example questions:[/bold]")
            for ex in EXAMPLES:
                console.print(f"  • {ex}")
            console.print()
            continue

        await chat(user_input)
        console.print()


if __name__ == "__main__":
    asyncio.run(main())
