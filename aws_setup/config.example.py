"""
Configuration template for the Cloud & Operations Lead AWS toolkit.
"""

# AWS region the lab account runs in
AWS_REGION = "us-west-2"

# 12-digit AWS account ID
ACCOUNT_ID = "616601120321"

# S3 bucket name
BUCKET_NAME = "urbanshift-data-1781521886-rjjrqj"

# The IAM permissions boundary ARN
PERMISSIONS_BOUNDARY_ARN = "PERMISSIONS_BOUNDARY_ARN"

# Local folder where the four raw data unzipped CSVs are
LOCAL_DATA_DIR = r"PATH_TO_UNZIPPED_CSVS"

# Names for the two IAM roles
PIPELINE_ROLE_NAME = "urbanshift-pipeline-rw"   # read-write, for the data pipeline
ANALYST_ROLE_NAME = "urbanshift-analyst-ro"     # read-only, for querying/modelling
