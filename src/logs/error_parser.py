import argparse
import json
import re
from collections import Counter
from pathlib import Path

PATTERNS = {
    "ERROR": re.compile(r"\bERROR\b", re.IGNORECASE),
    "WARN": re.compile(r"\bWARN(?:ING)?\b", re.IGNORECASE),
    "TIMEOUT": re.compile(r"\btimeout\b", re.IGNORECASE),
    "HTTP_500": re.compile(r"\b(?:HTTP\s*)?500\b", re.IGNORECASE),
}


def analyze_text(text: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for name, pattern in PATTERNS.items():
        counts[name] = len(pattern.findall(text))
    return dict(counts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize common application log signals.")
    parser.add_argument("logfile", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = args.logfile.read_text(encoding="utf-8", errors="replace")
    counts = analyze_text(text)

    if args.format == "json":
        print(json.dumps(counts, indent=2))
        return

    for key, value in counts.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
