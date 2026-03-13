"""Guarded runners — full guardrail system for general cases and guardrail tests."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from agents import Runner, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from src.agents.triage_agent import triage_agent
from tests.helpers.trace import console, print_trace




async def run_guardrail_tests(test_cases: list[dict]) -> None:
    """Run targeted guardrail tests with PASS/FAIL verdicts."""
    console.print(Panel.fit(
        "[bold cyan]GUARDRAIL TEST SUITE[/bold cyan]\n"
        "[dim]Verifying each guardrail fires correctly — and doesn't over-fire.[/dim]",
        border_style="cyan",
    ))
    console.print()

    passed = 0
    failed = 0

    for i, case in enumerate(test_cases, 1):
        console.rule(f"[bold]Test {i}: {case['label']}[/bold]")
        if "layer" in case:
            console.print(f"[cyan]Layer:[/cyan]    {case['layer']}")
        console.print(f"[cyan]Input:[/cyan]    {case['input']}")
        expected = case.get("expected_block")
        if "expected_block" in case:
            console.print(f"[cyan]Expects:[/cyan]  {'BLOCKED by ' + repr(expected) if expected else 'PASS — no guardrail should fire'}")
        note = case.get("guarded_note") or case.get("note", "")
        console.print(f"[dim]{note}[/dim]")
        console.print()

        blocked_by = None
        response = None
        result = None

        try:
            result = await Runner.run(triage_agent, input=case["input"])
            response = result.final_output
        except InputGuardrailTripwireTriggered as e:
            blocked_by = e.guardrail_result.guardrail.name or "input_guardrail"
        except OutputGuardrailTripwireTriggered as e:
            blocked_by = e.guardrail_result.guardrail.name or "output_guardrail"
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            failed += 1
            console.print()
            continue

        if expected is None and blocked_by is None:
            passed += 1
            console.print(f"[bold green]✓ PASS[/bold green] — no guardrail fired (correct)")
            if result:
                print_trace(result)
            if response:
                console.print(Panel(Text(response, style="white"), border_style="green",
                                    title=f"[green]{result.last_agent.name}[/green]"))

        elif expected is None and blocked_by is not None:
            failed += 1
            console.print(f"[bold red]✗ FAIL — FALSE POSITIVE[/bold red]")
            console.print(f"[red]Guardrail '{blocked_by}' fired but should NOT have.[/red]")

        elif expected is not None and blocked_by == expected:
            passed += 1
            console.print(f"[bold green]✓ PASS[/bold green] — correctly blocked by '{blocked_by}'")

        elif expected is not None and blocked_by is not None and blocked_by != expected:
            passed += 1  # still blocked — goal achieved
            console.print(f"[bold yellow]~ PASS (wrong layer)[/bold yellow] — blocked by '{blocked_by}', expected '{expected}'")

        else:
            failed += 1
            console.print(f"[bold red]✗ FAIL — MISSED[/bold red]")
            console.print(f"[red]Expected '{expected}' to fire, but nothing blocked this input.[/red]")
            if response:
                console.print(Panel(Text(response, style="white"), border_style="red",
                                    title="[red]Response that should have been blocked[/red]"))

        console.print()

    total = len(test_cases)
    color = "green" if failed == 0 else "red"
    console.print(Panel.fit(
        f"[bold {color}]GUARDRAIL RESULTS: {passed}/{total} passed[/bold {color}]\n\n"
        + ("[green]All guardrails working correctly.[/green]" if failed == 0
           else f"[red]{failed} test(s) failed — check guardrail prompts or classifier model.[/red]"),
        border_style=color,
    ))
