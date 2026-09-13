from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


def get_last_commits(limit: int = 5) -> list[str]:
    output = subprocess.check_output(
        ["git", "log", f"--pretty=format:%H", f"-{limit}"],
        text=True,
    ).strip()
    commits = [line for line in output.splitlines() if line]
    while len(commits) < limit:
        commits.append("not-available-yet")
    return commits


def main() -> None:
    path = Path("dev_sec_ops.yml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["git"]["latest_5_commits"] = get_last_commits(5)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print("dev_sec_ops.yml updated")


if __name__ == "__main__":
    main()
