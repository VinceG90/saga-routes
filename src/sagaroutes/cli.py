"""Development command-line interface for SagaRoutes."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

VALIDATORS = [
    "src/sagaroutes/validate_alignments.py",
    "src/sagaroutes/validate_places.py",
    "src/sagaroutes/validate_journeys.py",
]

EXPORTERS = [
    "src/sagaroutes/export_geojson.py",
    "src/sagaroutes/export_journeys.py",
    "src/sagaroutes/export_journey_routes.py",
]

class CommandError(Exception):
    """Raised when a SagaRoutes development command fails."""


def run_python_script(relative_path: str) -> None:
    """Run one project Python script and fail on nonzero exit."""

    script_path = REPOSITORY_ROOT / relative_path

    if not script_path.exists():
        raise CommandError(
            f"Required project script does not exist: "
            f"{relative_path}"
        )

    print()
    print(f"==> {relative_path}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=REPOSITORY_ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise CommandError(
            f"{relative_path} failed with exit code "
            f"{result.returncode}"
        )


def check_project() -> None:
    """Run all SagaRoutes validators."""

    print("SagaRoutes project validation")

    for validator in VALIDATORS:
        run_python_script(validator)

print()
print("All SagaRoutes validators passed.")

print()
print("Running automated tests")

result = subprocess.run(
    [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v",
    ],
    cwd=REPOSITORY_ROOT,
    check=False,
)

if result.returncode != 0:
    raise CommandError(
        "Automated test suite failed"
    )

print()
print("All SagaRoutes tests passed.")
def build_project() -> None:
    """Validate the project and regenerate derived exports."""

    check_project()

    print()
    print("Generating research exports")

    for exporter in EXPORTERS:
        run_python_script(exporter)

    print()
    print("SagaRoutes build completed successfully.")


def serve_project(
    host: str,
    port: int,
) -> None:
    """Build the project and run a local development server."""

    build_project()

    print()
    print(
        f"Serving SagaRoutes at "
        f"http://{host}:{port}/frontend/"
    )
    print("Press Ctrl+C to stop the server.")
    print()

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "http.server",
                str(port),
                "--bind",
                host,
            ],
            cwd=REPOSITORY_ROOT,
            check=True,
        )
    except KeyboardInterrupt:
        print()
        print("SagaRoutes development server stopped.")
    except subprocess.CalledProcessError as exc:
        raise CommandError(
            f"Development server exited with code "
            f"{exc.returncode}"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="sagaroutes",
        description=(
            "Validate, build, and serve the SagaRoutes prototype."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "check",
        help="Run all research-data validators.",
    )

    subparsers.add_parser(
        "build",
        help="Validate data and regenerate exports.",
    )

    serve_parser = subparsers.add_parser(
        "serve",
        help="Build and launch the local prototype.",
    )

    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP server bind address. Default: 127.0.0.1",
    )

    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP server port. Default: 8000",
    )

    return parser


def main() -> int:
    """Run the requested SagaRoutes development command."""

    parser = build_parser()
    arguments = parser.parse_args()

    try:
        if arguments.command == "check":
            check_project()

        elif arguments.command == "build":
            build_project()

        elif arguments.command == "serve":
            serve_project(
                arguments.host,
                arguments.port,
            )

        else:
            parser.error(
                f"Unknown command: {arguments.command}"
            )

    except CommandError as exc:
        print()
        print(
            f"SagaRoutes command failed: {exc}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
