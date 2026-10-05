#!/usr/bin/env python3
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone

FILE = os.environ.get("APPROVAL_FILE", "aproval.txt")

PLAN_DAYS = {"trial": 3, "monthly": 30, "quarterly": 90, "halfyear": 180, "yearly": 365}
ALIASES = {
    "trail": "trial", "free": "trial", "3day": "trial", "3days": "trial",
    "month": "monthly", "1month": "monthly",
    "quarter": "quarterly", "3month": "quarterly", "3months": "quarterly",
    "half": "halfyear", "half-year": "halfyear", "6month": "halfyear", "6months": "halfyear",
    "year": "yearly", "1year": "yearly", "12month": "yearly", "annual": "yearly",
}
SPLIT = re.compile(r"[\s,|;]+")


def today_utc() -> date:
    forced = os.environ.get("FAKE_TODAY")
    if forced:
        return date.fromisoformat(forced)
    return datetime.now(timezone.utc).date()


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def main() -> int:
    if not os.path.exists(FILE):
        print(f"{FILE} not found, nothing to do")
        return 0

    today = today_utc()
    with open(FILE, encoding="utf-8-sig") as fh:
        original = fh.read()

    out, stamped, removed = [], [], []
    for raw in original.splitlines():
        code, hash_, comment = raw.partition("#")
        parts = [p for p in SPLIT.split(code.strip()) if p]
        if len(parts) < 2:
            out.append(raw)
            continue

        plan = ALIASES.get(parts[1].lower(), parts[1].lower())
        days = PLAN_DAYS.get(plan)
        if days is None:
            out.append(raw)
            continue

        start = parse_date(parts[2]) if len(parts) > 2 else None
        if start is None:
            start = today
            stamped.append(parts[0])

        if today >= start + timedelta(days=days):
            removed.append(f"{parts[0]} {plan} {start}")
            continue

        new_line = f"{parts[0]} {plan} {start.isoformat()}"
        if hash_:
            new_line += f"  #{comment}"
        out.append(new_line)

    result = "\n".join(out)
    if original.endswith("\n") or result:
        result += "\n"

    if result != original:
        with open(FILE, "w", encoding="utf-8") as fh:
            fh.write(result)

    for k in stamped:
        print(f"stamped {today}: {k}")
    for line in removed:
        print(f"removed expired: {line}")
    if not stamped and not removed:
        print("no changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
