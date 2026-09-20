from pod_health import collect_pod_health, load_kube_context


def main() -> None:
    load_kube_context()
    rows = collect_pod_health()
    failed = [row for row in rows if row["phase"] == "Failed"]

    if not failed:
        print("No failed pods found.")
        return

    for row in failed:
        print(f"{row['namespace']} | {row['pod']} | restarts={row['restarts']}")


if __name__ == "__main__":
    main()
