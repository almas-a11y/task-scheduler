"""Task manager: add, update, complete, and delete tasks with schedule recalculation."""

from .task import Task, PriorityLevel
from .algorithm import build_schedule, detect_conflicts
from .storage import save_tasks, load_tasks
from datetime import datetime


def add_task(tasks: list[Task], task: Task) -> list[Task]:
    """Add a new task and return the updated list."""
    tasks.append(task)
    return tasks


def update_task(
    tasks: list[Task],
    task_id: str,
    name: str | None = None,
    deadline: datetime | None = None,
    duration: float | None = None,
    priority_level: PriorityLevel | None = None,
) -> list[Task]:
    """
    Update fields on an existing task by ID.
    Only provided (non-None) fields are changed.
    Raises ValueError if task_id is not found.
    """
    for task in tasks:
        if task.id == task_id:
            if name is not None:
                task.name = name
            if deadline is not None:
                task.deadline = deadline
            if duration is not None:
                task.duration = duration
            if priority_level is not None:
                task.priority_level = priority_level
            task.score = 0.0  # reset; recomputed on next get_schedule call
            return tasks
    raise ValueError(f"Task with id '{task_id}' not found.")


def complete_task(tasks: list[Task], task_id: str) -> list[Task]:
    """
    Mark a task as completed by ID.
    Raises ValueError if task_id is not found.
    """
    for task in tasks:
        if task.id == task_id:
            task.completed = True
            return tasks
    raise ValueError(f"Task with id '{task_id}' not found.")


def delete_task(tasks: list[Task], task_id: str) -> list[Task]:
    """
    Remove a task by ID.
    Raises ValueError if task_id is not found.
    """
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            return tasks
    raise ValueError(f"Task with id '{task_id}' not found.")


def get_schedule(tasks: list[Task]) -> tuple[list[Task], list[str]]:
    """
    Recompute scores and return (sorted_active_tasks, conflict_warnings).
    Completed tasks are excluded from the schedule.
    """
    schedule = build_schedule(tasks)
    warnings = detect_conflicts(schedule)
    return schedule, warnings


def save(tasks: list[Task], filepath: str = "tasks.json") -> None:
    """Persist all tasks to disk."""
    save_tasks(tasks, filepath)


def load(filepath: str = "tasks.json") -> list[Task]:
    """Load tasks from disk."""
    return load_tasks(filepath)
