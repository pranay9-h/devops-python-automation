import argparse
import csv
import json
from datetime import datetime
from typing import Any

import boto3


def collect_instances(region: str) -> list[dict[str, Any]]:
    ec2 = boto3.client("ec2", region_name=region)
    paginator = ec2.get_paginator("describe_instances")
    rows: list[dict[str, Any]] = []

    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                name = ""
                for tag in instance.get("Tags", []):
                    if tag.get("Key") == "Name":
                        name = tag.get("Value", "")
                        break

                launch_time = instance.get("LaunchTime")
                rows.append(
                    {
                        "instance_id": instance.get("InstanceId"),
                        "name": name,
                        "state": instance.get("State", {}).get("Name"),
                        "instance_type": instance.get("InstanceType"),
                        "availability_zone": instance.get("Placement", {}).get(
                            "AvailabilityZone"
                        ),
                        "launch_time": launch_time.isoformat()
                        if isinstance(launch_time, datetime)
                        else str(launch_time or ""),
                    }
                )
    return rows


def write_output(rows: list[dict[str, Any]], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(rows, indent=2))
        return

    if output_format == "csv":
        fieldnames = [
            "instance_id",
            "name",
            "state",
            "instance_type",
            "availability_zone",
            "launch_time",
        ]
        writer = csv.DictWriter(__import__("sys").stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return

    headers = ("Instance ID", "Name", "State", "Type", "AZ", "Launch Time")
    print(" | ".join(headers))
    print("-" * 100)
    for row in rows:
        print(
            f"{row['instance_id']} | {row['name']} | {row['state']} | "
            f"{row['instance_type']} | {row['availability_zone']} | {row['launch_time']}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List EC2 instances in a region.")
    parser.add_argument("--region", default="ap-south-1")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = collect_instances(args.region)
    write_output(rows, args.format)


if __name__ == "__main__":
    main()
