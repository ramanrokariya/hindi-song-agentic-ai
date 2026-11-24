# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

"""Execute PostgreSQL SQL verification scripts."""

import argparse
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_DIRECTORY = PROJECT_ROOT / "database" / "verification"

CONTAINER_NAME = "hindi-song-postgres"
DATABASE_NAME = "hindi_songs"
DATABASE_USER = "songadmin"


def verify_database_readiness():
    command = [
        "docker", "exec", CONTAINER_NAME,
        "pg_isready",
        "-U", DATABASE_USER,
        "-d", DATABASE_NAME,
    ]

    result = subprocess.run(command, check=False)

    return result.returncode == 0


def execute_sql_file(sql_file):
    command = [
        "docker", "exec", "-i", CONTAINER_NAME,
        "psql",
        "-v", "ON_ERROR_STOP=1",
        "-U", DATABASE_USER,
        "-d", DATABASE_NAME,
    ]

    with sql_file.open("r", encoding="utf-8") as source:
        result = subprocess.run(
            command,
            stdin=source,
            check=False,
        )

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Execute PostgreSQL verification scripts"
    )

    parser.add_argument(
        "--file",
        help="Execute an individual SQL verification file",
    )

    args = parser.parse_args()

    sql_files = sorted(SQL_DIRECTORY.glob("*.sql"))

    if args.file:
        sql_files = [
            path for path in sql_files
            if path.name == args.file
        ]

    if not sql_files:
        print("ERROR: No matching SQL verification files found.")
        return 1

    print("Checking PostgreSQL readiness...")

    try:
        if not verify_database_readiness():
            print("ERROR: PostgreSQL is not ready.")
            return 1
    except OSError as exc:
        print("ERROR:", exc)
        return 1

    passed = 0
    failed = 0

    for sql_file in sql_files:
        print("\n" + "=" * 60, flush=True)
        print("Executing:", sql_file.name, flush=True)
        print("=" * 60, flush=True)

        try:
            if execute_sql_file(sql_file):
                passed += 1
                print("PASS:", sql_file.name)
            else:
                failed += 1
                print("FAIL:", sql_file.name)

        except OSError as exc:
            failed += 1
            print("FAIL:", sql_file.name, exc)

    print("\n========== VERIFICATION SUMMARY ==========")
    print("Total SQL scripts:", len(sql_files))
    print("Passed:", passed)
    print("Failed:", failed)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
