"""
Step 3 — PROVE the read-only analyst role is correctly restricted.
"""

from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from _helpers import load_config


def main() -> None:
    cfg = load_config()
    role_arn = f"arn:aws:iam::{cfg.ACCOUNT_ID}:role/{cfg.ANALYST_ROLE_NAME}"

    print(f"Assuming read-only role: {role_arn}\n")
    s3 = _assume_role_s3_client(role_arn, cfg.AWS_REGION)

    results = []

    # POSITIVE check: the analyst is allowed to read curated/
    results.append(_expect_allow(
        "list objects under curated/",
        lambda: s3.list_objects_v2(Bucket=cfg.BUCKET_NAME, Prefix="curated/"),
    ))

    # NEGATIVE checks: each of these must be denied
    results.append(_expect_deny(
        "upload to raw/ (write to source-of-truth)",
        lambda: s3.put_object(Bucket=cfg.BUCKET_NAME, Key="raw/_denied_test.txt", Body=b"x"),
    ))
    results.append(_expect_deny(
        "upload to curated/ (analyst is read-only)",
        lambda: s3.put_object(Bucket=cfg.BUCKET_NAME, Key="curated/_denied_test.txt", Body=b"x"),
    ))
    results.append(_expect_deny(
        "delete from curated/",
        lambda: s3.delete_object(Bucket=cfg.BUCKET_NAME, Key="curated/customers/.keep"),
    ))

    # Summary
    print("\n" + "=" * 52)
    passed = sum(results)
    print(f"RESULT: {passed}/{len(results)} checks passed "
          f"({'restrictions work' if passed == len(results) else 'REVIEW YOUR POLICY'})")
    print("=" * 52)


def _assume_role_s3_client(role_arn: str, region: str):
    """Swap your own credentials for the analyst role's temporary credentials."""
    sts = boto3.client("sts")
    creds = sts.assume_role(RoleArn=role_arn, RoleSessionName="iam-restriction-test")["Credentials"]
    return boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
    )


def _expect_allow(label: str, action) -> bool:
    """An allowed action should succeed. Returns True on PASS."""
    try:
        action()
        print(f"  PASS  [allow] {label}")
        return True
    except ClientError as e:
        print(f"  FAIL  [allow] {label} was blocked: {e.response['Error']['Code']}")
        return False


def _expect_deny(label: str, action) -> bool:
    """A denied action should raise AccessDenied. Returns True on PASS (i.e. it was blocked)."""
    try:
        action()
        print(f"  FAIL  [deny ] {label} SUCCEEDED — policy is too permissive!")
        return False
    except ClientError as e:
        if e.response["Error"]["Code"] in ("AccessDenied", "AccessDeniedException"):
            print(f"  PASS  [deny ] {label} -> Access Denied (correct)")
            return True
        print(f"  ????  [deny ] {label} failed with unexpected error: {e.response['Error']['Code']}")
        return False


if __name__ == "__main__":
    main()
