#!/usr/bin/env python3
"""Validate knowledge base JSON files.

Usage:
    python hooks/validate_json.py <json_file> [json_file2 ...]

Examples:
    # Single file
    python hooks/validate_json.py knowledge/articles/2025-05-03_articles.json

    # Multiple files with glob pattern
    python hooks/validate_json.py knowledge/articles/*.json
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Optional, Union


REQUIRED_FIELDS: dict[str, type] = {
    "id": str,
    "title": str,
    "source_url": str,
    "summary": str,
    "tags": list,
    "status": str,
}

VALID_STATUS = {"draft", "review", "published", "archived"}
VALID_AUDIENCE = {"beginner", "intermediate", "advanced"}

ID_PATTERN = re.compile(r"^[a-z]+-\d{8}-\d{3}$")
URL_PATTERN = re.compile(r"^https?://\S+$")


class ValidationError:
    def __init__(self, file_path: Path, field: str, message: str):
        self.file_path = file_path
        self.field = field
        self.message = message

    def __str__(self) -> str:
        return f"{self.file_path}:{self.field}: {self.message}"


def validate_json_syntax(file_path: Path) -> tuple[Optional[Any], Optional[ValidationError]]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, ValidationError(file_path, "json", f"Invalid JSON: {e}")
    except Exception as e:
        return None, ValidationError(file_path, "file", f"Cannot read file: {e}")


def validate_required_fields(
    data: dict[str, Any],
    file_path: Path,
) -> list[ValidationError]:
    errors = []

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in data:
            errors.append(
                ValidationError(file_path, field, f"Missing required field")
            )
        elif not isinstance(data[field], expected_type):
            actual_type = type(data[field]).__name__
            errors.append(
                ValidationError(
                    file_path,
                    field,
                    f"Expected {expected_type.__name__}, got {actual_type}",
                )
            )

    return errors


def validate_id_format(id_value: str, file_path: Path) -> Optional[ValidationError]:
    if not ID_PATTERN.match(id_value):
        return ValidationError(
            file_path,
            "id",
            f"Invalid ID format. Expected: {{source}}-YYYYMMDD-NNN, got: {id_value}",
        )
    return None


def validate_status(status: str, file_path: Path) -> Optional[ValidationError]:
    if status not in VALID_STATUS:
        return ValidationError(
            file_path,
            "status",
            f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUS))}",
        )
    return None


def validate_url(url: str, file_path: Path) -> Optional[ValidationError]:
    if not URL_PATTERN.match(url):
        return ValidationError(
            file_path,
            "source_url",
            f"Invalid URL format. Must start with http:// or https://",
        )
    return None


def validate_summary(summary: str, file_path: Path) -> Optional[ValidationError]:
    if len(summary) < 20:
        return ValidationError(
            file_path,
            "summary",
            f"Summary too short. Minimum 20 characters, got {len(summary)}",
        )
    return None


def validate_tags(tags: list[Any], file_path: Path) -> Optional[ValidationError]:
    if len(tags) < 1:
        return ValidationError(
            file_path,
            "tags",
            f"At least 1 tag required, got {len(tags)}",
        )
    return None


def validate_score(score: Any, file_path: Path) -> Optional[ValidationError]:
    if not isinstance(score, (int, float)):
        return ValidationError(
            file_path,
            "score",
            f"Score must be a number, got {type(score).__name__}",
        )
    if not (1 <= score <= 10):
        return ValidationError(
            file_path,
            "score",
            f"Score must be between 1 and 10, got {score}",
        )
    return None


def validate_audience(audience: Any, file_path: Path) -> Optional[ValidationError]:
    if not isinstance(audience, str):
        return ValidationError(
            file_path,
            "audience",
            f"Audience must be a string, got {type(audience).__name__}",
        )
    if audience not in VALID_AUDIENCE:
        return ValidationError(
            file_path,
            "audience",
            f"Invalid audience. Must be one of: {', '.join(sorted(VALID_AUDIENCE))}",
        )
    return None


def validate_article(
    data: dict[str, Any],
    file_path: Path,
) -> list[ValidationError]:
    errors = []

    errors.extend(validate_required_fields(data, file_path))

    if "id" in data and isinstance(data["id"], str):
        if err := validate_id_format(data["id"], file_path):
            errors.append(err)

    if "status" in data and isinstance(data["status"], str):
        if err := validate_status(data["status"], file_path):
            errors.append(err)

    if "source_url" in data and isinstance(data["source_url"], str):
        if err := validate_url(data["source_url"], file_path):
            errors.append(err)

    if "summary" in data and isinstance(data["summary"], str):
        if err := validate_summary(data["summary"], file_path):
            errors.append(err)

    if "tags" in data and isinstance(data["tags"], list):
        if err := validate_tags(data["tags"], file_path):
            errors.append(err)

    if "score" in data:
        if err := validate_score(data["score"], file_path):
            errors.append(err)

    if "audience" in data:
        if err := validate_audience(data["audience"], file_path):
            errors.append(err)

    return errors


def validate_file(file_path: Path) -> list[ValidationError]:
    errors = []

    data, json_error = validate_json_syntax(file_path)
    if json_error:
        errors.append(json_error)
        return errors

    if isinstance(data, dict):
        errors.extend(validate_article(data, file_path))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            if isinstance(item, dict):
                item_errors = validate_article(item, file_path)
                for err in item_errors:
                    err.field = f"[{idx}].{err.field}"
                errors.extend(item_errors)
            else:
                errors.append(
                    ValidationError(
                        file_path,
                        f"[{idx}]",
                        f"Expected dict, got {type(item).__name__}",
                    )
                )
    else:
        errors.append(
            ValidationError(
                file_path,
                "root",
                f"Expected dict or list, got {type(data).__name__}",
            )
        )

    return errors


def expand_file_patterns(patterns: list[str]) -> list[Path]:
    files = []
    for pattern in patterns:
        path = Path(pattern)
        if path.exists():
            files.append(path)
        else:
            parent = path.parent if path.parent.exists() else Path(".")
            matched = list(parent.glob(path.name))
            if matched:
                files.extend(sorted(matched))
            else:
                print(f"Warning: No files match pattern: {pattern}", file=sys.stderr)

    return files


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python hooks/validate_json.py <json_file> [json_file2 ...]")
        return 1

    files = expand_file_patterns(sys.argv[1:])

    if not files:
        print("Error: No files to validate", file=sys.stderr)
        return 1

    all_errors: list[ValidationError] = []
    validated_count = 0
    failed_count = 0

    for file_path in files:
        errors = validate_file(file_path)

        if errors:
            failed_count += 1
            all_errors.extend(errors)
        else:
            validated_count += 1

    if all_errors:
        print("\nValidation Errors:\n")
        for error in all_errors:
            print(f"  {error}")

    print(f"\n{'=' * 60}")
    print(f"Validated: {validated_count} files")
    print(f"Failed:    {failed_count} files")
    print(f"Errors:    {len(all_errors)} total")
    print(f"{'=' * 60}\n")

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
