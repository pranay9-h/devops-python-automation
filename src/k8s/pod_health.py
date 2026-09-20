import argparse
from typing import Any

from kubernetes import client, config


def load_kube_context(context: str | None = None) -> None:
    try:
        config.load_kube_config(context=context)
    except config.ConfigException:
        config.load_incluster_config()


def collect_pod_health(
    namespace: str | None = None,
) -> list[dict[str, Any]]:
    v1 = client.CoreV1Api()
    pods = (
        v1.list_namespaced_pod(namespace)
        if namespace
        else v1.list_pod_for_all_namespaces()
    )

    results: list[dict[str, Any]] = []
    for pod in pods.items:
        restart_count = sum(
            status.restart_count or 0 for status in (pod.status.container_statuses or [])
        )

        waiting_reasons = [
            status.state.waiting.reason
            for status in (pod.status.container_statuses or [])
            if status.state and status.state.waiting and status.state.waiting.reason
        ]

        results.append(
            {
                "namespace": pod.metadata.namespace,
                "pod": pod.metadata.name,
                "phase": pod.status.phase,
                "restarts": restart_count,
                "waiting_reasons": waiting_reasons,
            }
        )
    return results


def unhealthy_reason(row: dict[str, Any], restart_threshold: int) -> str | None:
    if row["phase"] in {"Failed", "Pending", "Unknown"}:
        return f"phase={row['phase']}"

    if any(reason == "CrashLoopBackOff" for reason in row["waiting_reasons"]):
        return "CrashLoopBackOff"

    if row["restarts"] >= restart_threshold:
        return f"restarts={row['restarts']}"

    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report unhealthy Kubernetes pods.")
    parser.add_argument("--namespace")
    parser.add_argument("--context")
    parser.add_argument("--restart-threshold", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_kube_context(args.context)
    rows = collect_pod_health(args.namespace)

    unhealthy = []
    for row in rows:
        reason = unhealthy_reason(row, args.restart_threshold)
        if reason:
            unhealthy.append((row, reason))

    if not unhealthy:
        print("No unhealthy pods found.")
        return

    print("Namespace | Pod | Phase | Restarts | Reason")
    print("-" * 90)
    for row, reason in unhealthy:
        print(
            f"{row['namespace']} | {row['pod']} | {row['phase']} | "
            f"{row['restarts']} | {reason}"
        )


if __name__ == "__main__":
    main()
