#!/usr/bin/env python3
"""
Test runner script for MCP Client Console with coverage reporting.

This script provides various testing options including coverage reports,
different output formats, and selective test execution.
"""
import argparse
import subprocess
import sys


def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, check=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}", file=sys.stderr)
        print(f"Exit code: {e.returncode}", file=sys.stderr)
        if e.stdout:
            print(f"STDOUT: {e.stdout}", file=sys.stderr)
        if e.stderr:
            print(f"STDERR: {e.stderr}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests with various options")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--html", action="store_true", help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--xml", action="store_true", help="Generate XML coverage report"
    )
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--module",
        type=str,
        help="Run tests for specific module (e.g., service, exceptions)",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Run minimal coverage report (terminal only)",
    )

    args = parser.parse_args()

    # Base pytest command
    base_cmd = ["pytest"]

    # Add verbosity
    if args.verbose:
        base_cmd.append("-v")

    # Determine test path
    if args.unit:
        base_cmd.append("tests/unit/")
    elif args.integration:
        base_cmd.append("tests/integration/")
    elif args.module:
        base_cmd.append(f"tests/unit/test_{args.module}.py")
    else:
        base_cmd.append("tests/")

    # Add coverage options
    if args.coverage or args.html or args.xml or args.minimal:
        base_cmd.extend(
            [
                "--cov=core",
                "--cov=services",
                "--cov=connections",
                "--cov=utils",
                "--cov-report=term",
            ]
        )

        if args.html:
            base_cmd.append("--cov-report=html")

        if args.xml:
            base_cmd.append("--cov-report=xml")

        if not args.minimal and not args.html and not args.xml:
            # Default to terminal-missing for detailed coverage
            base_cmd.append("--cov-report=term-missing")

    # Run the command
    cmd = " ".join(base_cmd)
    print(f"Running: {cmd}")
    success = run_command(cmd)

    if success and (args.html or args.coverage):
        print("\n" + "=" * 50)
        print("Test Results Summary:")
        print("=" * 50)

        if args.html:
            print("📊 HTML coverage report generated in htmlcov/")
            print("   Open htmlcov/index.html in your browser")

        if args.xml:
            print("📄 XML coverage report generated as coverage.xml")

        print("✅ All tests completed successfully!")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
