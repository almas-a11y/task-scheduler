"""Unit tests for the task manager and edge cases."""

import pytest
from datetime import datetime, timedelta
from scheduler.task import Task
from scheduler.algorithm import build_schedule, detect_conflicts, compute_urgency_score
from scheduler.manager import (
    add_task,
    update_task,
    complete_task,
    delete_task,
    get_schedule,
)


def make_task(
    name: str,
    days: float,
    duration: float,
    level: str,
    completed: bool = False,
) -> Task:
    return Task(
        name=name,
        deadline=datetime.now() + timedelta(days=days),
        duration=duration,
        priority_level=level,
        completed=completed,
    )


# --- Edge cases: algorithm ---

def test_build_schedule_empty_list():
    assert build_schedule([]) == []

def test_build_schedule_all_completed():
    tasks = [
        make_task("Done1", days=1, duration=1, level="high", completed=True),
        make_task("Done2", days=2, duration=1, level="medium", completed=True),
    ]
    assert build_schedule(tasks) == []

def test_detect_conflicts_empty_schedule():
    assert detect_conflicts([]) == []

def test_urgency_overdue_negative_days():
    # Negative days (well past deadline) should still return 100
    assert compute_urgency_score(-5) == 100.0

def test_urgency_very_far_deadline():
    # 365 days out should return 0
    assert compute_urgency_score(365) == 0.0

def test_schedule_recalculates_after_update():
    """Score should change when deadline is updated closer."""
    task = make_task("T", days=20, duration=1, level="low")
    tasks = [task]
    schedule_before, _ = get_schedule(tasks)
    score_before = schedule_before[0].score

    update_task(tasks, task.id, deadline=datetime.now() + timedelta(days=1))
    schedule_after, _ = get_schedule(tasks)
    score_after = schedule_after[0].score

    assert score_after > score_before

def test_conflict_sorted_by_date():
    """Conflict warnings should be sorted by date (near deadline first)."""
    # Both groups have more hours than their available working window.
    # "near" deadline: due tomorrow (1 day = 8h available) with 10h of tasks.
    # "far" deadline: due in 2 days (2 days = 16h available) with 20h of tasks.
    near = datetime.now() + timedelta(days=1)
    far  = datetime.now() + timedelta(days=2)
    tasks = [
        Task(name="A", deadline=near, duration=6, priority_level="high"),
        Task(name="B", deadline=near, duration=6, priority_level="high"),
        Task(name="C", deadline=far,  duration=11, priority_level="high"),
        Task(name="D", deadline=far,  duration=11, priority_level="high"),
    ]
    warnings = detect_conflicts(tasks)
    assert len(warnings) == 2
    assert warnings[0] < warnings[1]  # near date string < far date string


# --- Manager: add ---

def test_add_task():
    tasks = []
    t = make_task("New task", days=5, duration=2, level="medium")
    add_task(tasks, t)
    assert len(tasks) == 1
    assert tasks[0].name == "New task"

def test_add_multiple_tasks():
    tasks = []
    for i in range(3):
        add_task(tasks, make_task(f"Task {i}", days=i+1, duration=1, level="low"))
    assert len(tasks) == 3


# --- Manager: update ---

def test_update_task_name():
    tasks = [make_task("Old name", days=5, duration=1, level="low")]
    update_task(tasks, tasks[0].id, name="New name")
    assert tasks[0].name == "New name"

def test_update_task_duration():
    tasks = [make_task("T", days=5, duration=1.0, level="low")]
    update_task(tasks, tasks[0].id, duration=4.0)
    assert tasks[0].duration == 4.0

def test_update_task_priority():
    tasks = [make_task("T", days=5, duration=1, level="low")]
    update_task(tasks, tasks[0].id, priority_level="high")
    assert tasks[0].priority_level == "high"

def test_update_task_resets_score():
    tasks = [make_task("T", days=5, duration=1, level="low")]
    tasks[0].score = 99.0
    update_task(tasks, tasks[0].id, name="Updated")
    assert tasks[0].score == 0.0

def test_update_task_not_found():
    tasks = [make_task("T", days=5, duration=1, level="low")]
    with pytest.raises(ValueError):
        update_task(tasks, "nonexistent-id", name="X")

def test_update_partial_fields_unchanged():
    tasks = [make_task("T", days=5, duration=3.0, level="medium")]
    update_task(tasks, tasks[0].id, name="Updated")
    assert tasks[0].duration == 3.0
    assert tasks[0].priority_level == "medium"


# --- Manager: complete ---

def test_complete_task():
    tasks = [make_task("T", days=3, duration=1, level="high")]
    complete_task(tasks, tasks[0].id)
    assert tasks[0].completed is True

def test_complete_task_excluded_from_schedule():
    tasks = [
        make_task("Active", days=2, duration=1, level="low"),
        make_task("Done", days=1, duration=1, level="high"),
    ]
    complete_task(tasks, tasks[1].id)
    schedule, _ = get_schedule(tasks)
    assert len(schedule) == 1
    assert schedule[0].name == "Active"

def test_complete_task_not_found():
    tasks = [make_task("T", days=3, duration=1, level="high")]
    with pytest.raises(ValueError):
        complete_task(tasks, "bad-id")


# --- Manager: delete ---

def test_delete_task():
    tasks = [make_task("T", days=3, duration=1, level="high")]
    task_id = tasks[0].id
    delete_task(tasks, task_id)
    assert len(tasks) == 0

def test_delete_task_not_found():
    tasks = [make_task("T", days=3, duration=1, level="high")]
    with pytest.raises(ValueError):
        delete_task(tasks, "bad-id")

def test_delete_only_removes_target():
    tasks = [
        make_task("Keep", days=5, duration=1, level="low"),
        make_task("Remove", days=2, duration=1, level="high"),
    ]
    delete_task(tasks, tasks[1].id)
    assert len(tasks) == 1
    assert tasks[0].name == "Keep"


# --- Complex scenario: mixed workload ---

def test_complex_scenario_conflict_after_add():
    """Adding heavy tasks to the same day should trigger a conflict warning."""
    same_day = datetime.now() + timedelta(days=1)
    tasks = []
    for i in range(4):
        t = Task(name=f"Task {i}", deadline=same_day, duration=3.0, priority_level="medium")
        add_task(tasks, t)
    _, warnings = get_schedule(tasks)
    assert len(warnings) == 1
    assert "Warning" in warnings[0]

def test_complex_scenario_completing_resolves_conflict():
    """Marking tasks complete should remove them from conflict calculation."""
    same_day = datetime.now() + timedelta(days=1)
    tasks = [
        Task(name="Heavy1", deadline=same_day, duration=5.0, priority_level="high"),
        Task(name="Heavy2", deadline=same_day, duration=5.0, priority_level="high"),
    ]
    _, warnings_before = get_schedule(tasks)
    assert len(warnings_before) == 1

    complete_task(tasks, tasks[0].id)
    _, warnings_after = get_schedule(tasks)
    assert len(warnings_after) == 0
