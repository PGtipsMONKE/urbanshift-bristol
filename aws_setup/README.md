# AWS Setup Toolkit - Cloud & Operations Lead

## Overview

The IAM roles are not implemented but this document and directory provides an example of how it may be done. This is theoretical and has not been tested, but should still show how IAM roles could be set up and the S3 bucket managed/

## Files

```
aws_setup/
├── README.md                  <- you are here
├── config.example.py          <- copy to config.py, fill in your values
├── _helpers.py                <- shared loader
├── s3_structure.py            <- Step 1: create prefixes + upload raw CSVs
├── create_iam_roles.py        <- Step 2: create the 2 roles + boundary
├── test_iam_restrictions.py   <- Step 3: prove the read-only role is locked down
└── iam_policies/
    ├── trust_policy.json           <- who may assume the roles
    ├── pipeline_role_policy.json   <- read-write (least privilege)
    └── analyst_role_policy.json    <- read-only on curated/
```

## Run order

```bash
python s3_structure.py          # Step 1 — build the bucket structure
python create_iam_roles.py      # Step 2 — create the two roles
python test_iam_restrictions.py # Step 3 — prove the restrictions work
```

## The IAM design

**Principle: least privilege.** Each role gets the minimum access it needs.

**Pipeline role (read-write)**
- `raw/`: read + upload, but no delete. `raw/` is the source of truth; making it write-once means nobody can accidentally destroy the original data.
- `curated/`: full access (read, write, overwrite) because cleaned outputs get regenerated.

**Analyst role (read-only)**
- `curated/`: read only.
- Cannot write anywhere and cannot see `raw/` at all.

**Permissions boundary** — attached to both roles. Even if a policy is more generous than intended, the boundary blocks the extra access, `create_iam_roles.py` applies it on every role.


### Service permissions beyond S3
These scripts scope S3 access precisely. The pipeline role will also need DataBrew / Data Wrangler / Redshift-load permissions, and the analyst role will need Redshift-query / Canvas, to be added  as AWS managed policies.