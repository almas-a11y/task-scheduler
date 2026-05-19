"""Persist and load tasks using a local JSON file."""

import json
import os
from .task import Task

DEFAULT_PATH = "tasks.json"


def save_tasks(tasks: list[Task], filepath: str = DEFAULT_PATH) -> None:
    """Serialize tasks to JSON and write to disk."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)


def load_tasks(filepath: str = DEFAULT_PATH) -> list[Task]:
    """Load tasks from JSON file. Returns empty list if file not found."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Task.from_dict(d) for d in data]
