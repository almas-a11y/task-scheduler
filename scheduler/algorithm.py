"""Priority scoring and scheduling algorithm."""

from datetime import datetime
from .task import Task, PRIORITY_WEIGHTS

# Urgency drops to 0 at or beyond this many days
MAX_URGENCY_DAYS: float = 30.0

# Score blend weights (must sum to 1.0)
URGENCY_WEIGHT: float = 0.6
IMPORTANCE_WEIGHT: float = 0.4


def compute_urgency_score(days_remaining: float) -> float:
    """Return 0–100: higher when deadline is closer. Overdue tasks score 100."""
    if days_remaining <= 0:
        return 100.0
    if days_remaining >= MAX_URGENCY_DAYS:
        return 0.0
    return round((1 - days_remaining / MAX_URGENCY_DAYS) * 100, 2)


def compute_priority_score(task: Task) -> float:
    """Compute and return the blended priority score (0–100)."""
    urgency = compute_urgency_score(task.days_until_deadline())
    importance = PRIORITY_WEIGHTS[task.priority_level]
    return round(URGENCY_WEIGHT * urgency + IMPORTANCE_WEIGHT * importance, 2)


def score_tasks(tasks: list[Task]) -> list[Task]:
    """Compute scores for all tasks in place and return them."""
    for task in tasks:
        task.score = compute_priority_score(task)
    return tasks


def build_schedule(tasks: list[Task]) -> list[Task]:
    """
    Return active tasks sorted by priority score (highest first).
    Returns empty list if tasks is empty or all tasks are completed.
    """
    if not tasks:
        return []
    active = [t for t in tasks if not t.completed]
    if not active:
        return []
    scored = score_tasks(active)
    return sorted(scored, key=lambda t: t.score, reverse=True)


def build_today_plan(schedule: list[Task], available_hours: float = 8.0) -> list[Task]:
    """
    Return the tasks to work on today.
    Overdue tasks are always included first (they can't wait).
    Remaining hours are filled greedily with highest-priority upcoming tasks.
    """
    today = datetime.now().date()
    overdue  = [t for t in schedule if t.deadline.date() < today]
    upcoming = [t for t in schedule if t.deadline.date() >= today]

    plan = list(overdue)
    remaining = available_hours - sum(t.duration for t in overdue)

    for task in upcoming:
        if task.duration <= remaining:
            plan.append(task)
            remaining -= task.duration

    return plan


def detect_conflicts(schedule: list[Task], available_hours_per_day: float = 8.0) -> list[str]:
    """
    Warn if tasks due on the same day exceed total available working hours
    between today and that deadline. A task due in 30 days has 30 days worth
    of working hours available, not just 8.
    Returns a list of warning strings. Returns empty list if schedule is empty.
    """
    if not schedule:
        return []

    warnings: list[str] = []
    day_load: dict[str, float] = {}
    today = datetime.now().date()

    for task in schedule:
        day_key = task.deadline.strftime("%Y-%m-%d")
        day_load[day_key] = day_load.get(day_key, 0.0) + task.duration

    for day_str, total_hours in sorted(day_load.items()):
        deadline_date = datetime.strptime(day_str, "%Y-%m-%d").date()
        days_available = max(1, (deadline_date - today).days)
        available_hours = days_available * available_hours_per_day
        if total_hours > available_hours:
            warnings.append(
                f"Warning: {total_hours:.1f}h of tasks due {day_str} "
                f"but only {available_hours:.0f}h available ({days_available} days)."
            )
    return warnings
