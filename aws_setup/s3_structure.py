"""
Step 1 — Create the S3 bucket structure and upload the raw CSVs.

Layout it creates:

    s3://<bucket>/
    ├── raw/        <- the 4 original CSVs, uploaded once, never edited
    │   ├── customers/customers.csv
    │   ├── couriers/couriers.csv
    │   ├── deliveries/deliveries.csv
    │   └── incidents/incidents.csv
    └── curated/    <- cleaned outputs land here

"""
from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from _helpers import load_config

# the four source files and the prefix each belongs under
SOURCES = ["customers", "couriers", "deliveries", "incidents"]


def main() -> None:
    cfg = load_config()
    s3 = boto3.client("s3", region_name=cfg.AWS_REGION)
    data_dir = cfg.LOCAL_DATA_DIR

    print(f"Bucket: {cfg.BUCKET_NAME}  (region {cfg.AWS_REGION})\n")

    # upload the raw CSVs
    for source in SOURCES:
        key = f"raw/{source}/{source}.csv"
        local_path = f"{data_dir}\\{source}.csv"  # Windows path; adjust if on Mac/Linux

        if _object_exists(s3, cfg.BUCKET_NAME, key):
            # protect raw/ from accidental overwrites.
            print(f"  SKIP  {key} already exists (raw/ is write-once)")
            continue

        try:
            s3.upload_file(local_path, cfg.BUCKET_NAME, key)
            print(f"  PUT   {key}")
        except FileNotFoundError:
            print(f"  ERROR file not found: {local_path} — check LOCAL_DATA_DIR in config.py")
        except ClientError as e:
            print(f"  ERROR uploading {key}: {e}")

    # create the empty curated/ structure
    for source in SOURCES:
        placeholder = f"curated/{source}/.keep"
        s3.put_object(Bucket=cfg.BUCKET_NAME, Key=placeholder, Body=b"")
        print(f"  PUT   {placeholder}")

    # confirm what's in the bucket
    print("\nBucket contents:")
    resp = s3.list_objects_v2(Bucket=cfg.BUCKET_NAME)
    for obj in resp.get("Contents", []):
        print(f"  {obj['Key']}  ({obj['Size']} bytes)")


def _object_exists(s3, bucket: str, key: str) -> bool:
    """Return True if the object already exists in the bucket."""
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


if __name__ == "__main__":
    main()
