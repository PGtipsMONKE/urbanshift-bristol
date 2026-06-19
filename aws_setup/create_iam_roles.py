"""
Step 2 — Create the two IAM roles with the permissions boundary applied.

Two roles, designed for LEAST PRIVILEGE (each gets only what it needs):

  1. PIPELINE role (read-write)  -> builds the pipeline
        - read + upload to raw/        (but NOT delete — raw/ is write-once)
        - full access to curated/      (read, write, overwrite cleaned outputs)

  2. ANALYST role (read-only)    -> queries and models the curated data
        - read curated/ only
        - cannot write anywhere, cannot touch raw/

Both roles get the PERMISSIONS BOUNDARY attached — a ceiling that caps what the
role can ever do, even if a policy is broader than intended.
"""
from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from _helpers import load_config, load_policy


def main() -> None:
    cfg = load_config()
    iam = boto3.client("iam", region_name=cfg.AWS_REGION)

    trust_policy = load_policy("trust_policy.json", ACCOUNT_ID=cfg.ACCOUNT_ID)

    create_role(
        iam, cfg,
        role_name=cfg.PIPELINE_ROLE_NAME,
        trust_policy=trust_policy,
        permission_policy=load_policy("pipeline_role_policy.json", BUCKET_NAME=cfg.BUCKET_NAME),
        description="UrbanShift pipeline role: read-write S3, builds the data pipeline.",
    )

    create_role(
        iam, cfg,
        role_name=cfg.ANALYST_ROLE_NAME,
        trust_policy=trust_policy,
        permission_policy=load_policy("analyst_role_policy.json", BUCKET_NAME=cfg.BUCKET_NAME),
        description="UrbanShift analyst role: read-only on curated/, for querying and modelling.",
    )

    print("\nDone. Next: run test_iam_restrictions.py to prove the analyst role is locked down.")


def create_role(iam, cfg, role_name, trust_policy, permission_policy, description) -> None:
    """Create one role with the permissions boundary, then attach its inline policy."""
    try:
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=trust_policy,
            PermissionsBoundary=cfg.PERMISSIONS_BOUNDARY_ARN,
            Description=description,
            MaxSessionDuration=3600,
        )
        print(f"CREATED role {role_name} (boundary applied)")
    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            print(f"EXISTS  role {role_name} — leaving it in place")
        else:
            raise

    # attach the fine-grained S3 permissions as an inline policy.
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=f"{role_name}-s3-access",
        PolicyDocument=permission_policy,
    )
    print(f"        attached S3 access policy to {role_name}")

# add these as AWS managed policies
    # # PIPELINE role typically also needs DataBrew / Data Wrangler / Redshift load:
    # iam.attach_role_policy(RoleName=role_name,
    #     PolicyArn="arn:aws:iam::aws:policy/AwsGlueDataBrewFullAccessPolicy")
    #
    # # ANALYST role typically also needs read-only Redshift query + Canvas:
    # iam.attach_role_policy(RoleName=role_name,
    #     PolicyArn="arn:aws:iam::aws:policy/AmazonRedshiftReadOnlyAccess")


if __name__ == "__main__":
    main()
