# Project: Hindi Song Agentic AI Search Engine
# Author: Raman Rokariya
# Book: Building an Agentic AI Song Search Engine
# Release: Volume 1 - v1.0-book

"""Identify Python imports and installed distribution versions."""

import ast
import sys
from importlib.metadata import (
    packages_distributions,
    version,
    PackageNotFoundError,
)
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_DIRECTORIES = [
    "backend",
    "scripts",
    "tests",
]


def collect_imports(directory):
    imports = set()

    for source_file in sorted(directory.rglob("*.py")):
        tree = ast.parse(
            source_file.read_text(encoding="utf-8"),
            filename=str(source_file),
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    imports.add(node.module.split(".")[0])

    return imports


def main():
    distributions = packages_distributions()
    standard_library = sys.stdlib_module_names

    print("Python version:", sys.version.split()[0])

    for directory_name in SOURCE_DIRECTORIES:
        directory = PROJECT_ROOT / directory_name

        print("\n" + "=" * 60)
        print("Directory:", directory_name)
        print("=" * 60)

        if not directory.exists():
            print("Directory not found")
            continue

        imports = collect_imports(directory)

        for module in sorted(imports):
            if module in standard_library:
                continue

            if module in SOURCE_DIRECTORIES:
                continue

            package_names = distributions.get(module, [])

            if not package_names:
                print(f"{module}: unresolved or local module")
                continue

            for package_name in sorted(package_names):
                try:
                    installed_version = version(package_name)

                    print(
                        f"{module:<20} "
                        f"{package_name}=={installed_version}"
                    )

                except PackageNotFoundError:
                    print(f"{package_name}: version unavailable")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
