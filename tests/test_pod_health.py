from k8s.pod_health import unhealthy_reason


def test_crashloop_is_unhealthy():
    row = {
        "phase": "Running",
        "restarts": 2,
        "waiting_reasons": ["CrashLoopBackOff"],
    }

    assert unhealthy_reason(row, restart_threshold=5) == "CrashLoopBackOff"


def test_restart_threshold_is_unhealthy():
    row = {
        "phase": "Running",
        "restarts": 7,
        "waiting_reasons": [],
    }

    assert unhealthy_reason(row, restart_threshold=5) == "restarts=7"


def test_healthy_pod_returns_none():
    row = {
        "phase": "Running",
        "restarts": 0,
        "waiting_reasons": [],
    }

    assert unhealthy_reason(row, restart_threshold=5) is None
