"""
Small shared helpers for the AWS setup scripts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

POLICY_DIR = Path(__file__).parent / "iam_policies"


def load_config():
    """Import config.py and refuse to run if the placeholders weren't filled in."""
    try:
        import config
    except ModuleNotFoundError:
        sys.exit(
            "ERROR: config.py not found.\n"
            "Copy config.example.py to config.py and fill in your group's values."
        )

    # catch running before filling in the values.
    leftover = [k for k, v in vars(config).items()
                if isinstance(v, str) and v.startswith("TODO_")]
    if leftover:
        sys.exit(
            "ERROR: these values in config.py are still placeholders: "
            + ", ".join(leftover)
        )
    return config


def load_policy(filename: str, **substitutions) -> str:
    """
    Read a policy JSON template and replace {{PLACEHOLDERS}} with real values.

    Example: load_policy("pipeline_role_policy.json", BUCKET_NAME="my-bucket")
    Returns a JSON *string* because that is what boto3's IAM calls expect.
    """
    text = (POLICY_DIR / filename).read_text(encoding="utf-8")
    for key, value in substitutions.items():
        text = text.replace("{{" + key + "}}", value)

    # fail loudly if a placeholder was missed, rather than sending bad JSON to AWS
    if "{{" in text:
        raise ValueError(f"{filename} still contains an unfilled placeholder: {text}")

    json.loads(text)  # validates the JSON is well-formed before use
    return text
