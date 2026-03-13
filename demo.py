"""
Physics Tutor Demo — guarded and unguarded modes in one file.

Usage:
  python demo.py --mode unguarded          # test_case_1, no guardrails (Phase 1)
  python demo.py --mode guarded --cases 1  # test_case_1 through the guardrail system
  python demo.py --mode guarded --cases 2  # test_case_2 only
  python demo.py --mode guarded            # all cases — test_case_1 + test_case_2
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
        help="Which test-case set: 1=test_case_1, 2=test_case_2 (default: all for guarded, 1 for unguarded)",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    if args.mode == "unguarded":
        cases = TEST_CASE_1 if args.cases != "2" else TEST_CASE_2
        await run_unguarded(
            cases,
            title="THE UNGUARDED AGENT",
            subtitle="No guardrails. No safety net. Watch what happens.",
        )
    else:
        # guarded: default runs all cases combined
        if args.cases == "1":
            cases = TEST_CASE_1
        elif args.cases == "2":
            cases = TEST_CASE_2
        else:
            cases = TEST_CASE_1 + TEST_CASE_2  # all
        await run_guardrail_tests(cases)


if __name__ == "__main__":
    asyncio.run(main())
