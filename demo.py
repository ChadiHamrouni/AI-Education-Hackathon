"""
Physics Tutor Demo — guarded and unguarded modes in one file.

Usage:
  python demo.py                      # guarded + test_case_2 (default)
  python demo.py --mode unguarded     # unguarded + test_case_1
  python demo.py --mode guarded --cases 1   # guarded, run test_case_1
  python demo.py --mode guarded --cases 2   # guarded, run test_case_2
  python demo.py --mode unguarded --cases 2 # unguarded, run test_case_2
"""

import argparse
import asyncio

from tests.cases.test_case_1 import TEST_CASE_1
from tests.cases.test_case_2 import TEST_CASE_2
from tests.runners.run_guarded import run_guardrail_tests
from tests.runners.run_unguarded import run_unguarded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Physics Tutor Demo")
    parser.add_argument(
        "--mode",
        choices=["guarded", "unguarded"],
        default="guarded",
        help="Which agent pipeline to use (default: guarded)",
    )
    parser.add_argument(
        "--cases",
        choices=["1", "2"],
        default=None,
        help="Which test-case set to run: 1=unguarded cases, 2=guardrail suite (default: matches mode)",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    # default: unguarded mode → test_case_1, guarded mode → test_case_2
    cases_choice = args.cases or ("2" if args.mode == "guarded" else "1")
    cases = TEST_CASE_1 if cases_choice == "1" else TEST_CASE_2

    if args.mode == "guarded":
        await run_guardrail_tests(cases)
    else:
        await run_unguarded(
            cases,
            title="THE UNGUARDED AGENT",
            subtitle="No guardrails. No safety net. Watch what happens.",
        )


if __name__ == "__main__":
    asyncio.run(main())
