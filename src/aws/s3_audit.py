import argparse
from typing import Any

import boto3


def audit_buckets() -> list[dict[str, Any]]:
    s3 = boto3.client("s3")
    buckets = s3.list_buckets().get("Buckets", [])
    results: list[dict[str, Any]] = []

    for bucket in buckets:
        name = bucket["Name"]
        try:
            encryption = s3.get_bucket_encryption(Bucket=name)
            rules = encryption.get("ServerSideEncryptionConfiguration", {}).get(
                "Rules", []
            )
            encrypted = bool(rules)
        except s3.exceptions.ClientError:
            encrypted = False

        try:
            pab = s3.get_public_access_block(Bucket=name)["PublicAccessBlockConfiguration"]
            public_blocked = all(
                pab.get(key, False)
                for key in (
                    "BlockPublicAcls",
                    "IgnorePublicAcls",
                    "BlockPublicPolicy",
                    "RestrictPublicBuckets",
                )
            )
        except s3.exceptions.ClientError:
            public_blocked = False

        results.append(
            {
                "bucket": name,
                "encrypted": encrypted,
                "public_access_blocked": public_blocked,
            }
        )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit basic S3 security posture.")
    parser.parse_args()

    results = audit_buckets()
    if not results:
        print("No S3 buckets found.")
        return

    for item in results:
        print(
            f"{item['bucket']} | encrypted={item['encrypted']} | "
            f"public_access_blocked={item['public_access_blocked']}"
        )


if __name__ == "__main__":
    main()
