"""Verify local file and module references in project documentation."""

import importlib.util
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOCUMENTS = [
    "UsefulCommands.txt",
    "README.md",
    "scripts/README.md",
    "tests/README.md",
    "database/verification/README.md",
]

FILE_PATTERN = re.compile(
    r"(?<![\w/])"
    r"(?:backend|database|scripts|tests)/"
    r"[\w./-]+\.(?:py|sql|md|json)\b"
)

MODULE_PATTERN = re.compile(
    r"\bpython(?:3)?\s+-m\s+([\w.]+)"
)

LINK_PATTERN = re.compile(
    r"\[[^\]]+\]\(([^)\s]+)\)"
)

MANIFEST_PATTERN = re.compile(
    r"\brequirements(?:-dev|-lock)?\.txt\b"
)


def main():
    checked = set()
    failures = []

    def record(document, reference, exists):
        key = (document, reference)

        if key in checked:
            return

        checked.add(key)

        if exists:
            print(f"PASS: {document} -> {reference}")
        else:
            print(f"FAIL: {document} -> {reference}")
            failures.append(key)

    for document in DOCUMENTS:
        path = PROJECT_ROOT / document

        if not path.is_file():
            record(document, document, False)
            continue

        content = path.read_text(encoding="utf-8")

        print(f"\nChecking: {document}")

        for reference in sorted(set(FILE_PATTERN.findall(content))):
            record(
                document,
                reference,
                (PROJECT_ROOT / reference).is_file(),
            )

        for module in sorted(set(MODULE_PATTERN.findall(content))):
            if module.startswith("backend."):
                relative = module.replace(".", "/")
                exists = (
                    (PROJECT_ROOT / f"{relative}.py").is_file()
                    or
                    (PROJECT_ROOT / relative / "__init__.py").is_file()
                )
            else:
                try:
                    exists = importlib.util.find_spec(module) is not None
                except (ImportError, ValueError, AttributeError):
                    exists = False

            record(document, f"module:{module}", exists)

        for reference in sorted(set(MANIFEST_PATTERN.findall(content))):
            record(
                document,
                reference,
                (PROJECT_ROOT / reference).is_file(),
            )

        if path.suffix == ".md":
            for link in sorted(set(LINK_PATTERN.findall(content))):
                if link.startswith((
                    "http://", "https://", "mailto:", "#"
                )):
                    continue

                target = link.split("#", 1)[0]

                if target:
                    record(
                        document,
                        f"link:{link}",
                        (path.parent / target).exists(),
                    )

    print("\n" + "=" * 60)
    print("DOCUMENTATION REFERENCE VERIFICATION")
    print("=" * 60)
    print(f"Total references: {len(checked)}")
    print(f"Passed: {len(checked) - len(failures)}")
    print(f"Failed: {len(failures)}")

    if failures:
        print("\nReferences requiring review:")

        for document, reference in failures:
            print(f"  {document}: {reference}")

        return 1

    print("\nALL DOCUMENTATION REFERENCE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
