import argparse
from typing import Any

import boto3


def find_unattached_volumes(region: str) -> list[dict[str, Any]]:
    ec2 = boto3.client("ec2", region_name=region)
    paginator = ec2.get_paginator("describe_volumes")
    results: list[dict[str, Any]] = []

    for page in paginator.paginate(
        Filters=[{"Name": "status", "Values": ["available"]}]
    ):
        for volume in page.get("Volumes", []):
            results.append(
                {
                    "volume_id": volume["VolumeId"],
                    "size_gib": volume["Size"],
                    "volume_type": volume["VolumeType"],
                    "availability_zone": volume["AvailabilityZone"],
                    "encrypted": volume.get("Encrypted", False),
                }
            )
    return results


def delete_volumes(
    region: str, volumes: list[dict[str, Any]], confirm: bool = False
) -> None:
    if not confirm:
        print("Dry-run mode: no resources will be deleted.")
        return

    ec2 = boto3.client("ec2", region_name=region)
    for volume in volumes:
        volume_id = volume["volume_id"]
        ec2.delete_volume(VolumeId=volume_id)
        print(f"Deleted {volume_id}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find unattached EBS volumes. Deletion is opt-in."
    )
    parser.add_argument("--region", default="ap-south-1")
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete discovered unattached volumes after explicit confirmation.",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required with --delete to perform deletion.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    volumes = find_unattached_volumes(args.region)

    if not volumes:
        print("No unattached EBS volumes found.")
        return

    print(f"Found {len(volumes)} unattached volume(s):")
    for volume in volumes:
        print(
            f"{volume['volume_id']} | {volume['size_gib']} GiB | "
            f"{volume['volume_type']} | {volume['availability_zone']} | "
            f"encrypted={volume['encrypted']}"
        )

    if args.delete and args.confirm:
        delete_volumes(args.region, volumes, confirm=True)
    else:
        print("No resources were deleted.")
        if args.delete:
            print("Deletion requires both --delete and --confirm.")


if __name__ == "__main__":
    main()
