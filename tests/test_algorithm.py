"""Unit tests for the priority scoring and scheduling algorithm."""

import pytest
from datetime import datetime, timedelta
from scheduler.task import Task
from scheduler.algorithm import (
    compute_urgency_score,
    compute_priority_score,
    build_schedule,
    detect_conflicts,
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


# --- Urgency score ---

def test_urgency_overdue():
    assert compute_urgency_score(0) == 100.0

def test_urgency_far_deadline():
    assert compute_urgency_score(30) == 0.0

def test_urgency_midpoint():
    score = compute_urgency_score(15)
    assert 49 < score < 51  # ~50

def test_urgency_beyond_max():
    assert compute_urgency_score(60) == 0.0


# --- Priority score ---

def test_priority_score_range():
    task = make_task("T", days=5, duration=2, level="high")
    score = compute_priority_score(task)
    assert 0.0 <= score <= 100.0

def test_high_priority_beats_low_same_deadline():
    high = make_task("High", days=5, duration=1, level="high")
    low = make_task("Low", days=5, duration=1, level="low")
    assert compute_priority_score(high) > compute_priority_score(low)

def test_closer_deadline_beats_further_same_priority():
    close = make_task("Close", days=1, duration=1, level="medium")
    far = make_task("Far", days=20, duration=1, level="medium")
    assert compute_priority_score(close) > compute_priority_score(far)


# --- build_schedule ---

def test_schedule_excludes_completed():
    tasks = [
        make_task("Done", days=1, duration=1, level="high", completed=True),
        make_task("Active", days=5, duration=1, level="low"),
    ]
    schedule = build_schedule(tasks)
    assert len(schedule) == 1
    assert schedule[0].name == "Active"

def test_schedule_sorted_descending():
    tasks = [
        make_task("Low urgency", days=25, duration=1, level="low"),
        make_task("High urgency", days=1, duration=1, level="high"),
        make_task("Medium", days=10, duration=1, level="medium"),
    ]
    schedule = build_schedule(tasks)
    scores = [t.score for t in schedule]
    assert scores == sorted(scores, reverse=True)


# --- detect_conflicts ---

def test_no_conflict():
    tasks = [make_task("T1", days=1, duration=2, level="low")]
    warnings = detect_conflicts(tasks, available_hours_per_day=8)
    assert warnings == []

def test_conflict_detected():
    # Two tasks due tomorrow totalling 10h — only 1 working day (8h) available.
    same_day = datetime.now() + timedelta(days=1)
    tasks = [make_task("T1", days=1, duration=5, level="high"),
             make_task("T2", days=1, duration=5, level="medium")]
    tasks[0].deadline = same_day
    tasks[1].deadline = same_day
    warnings = detect_conflicts(tasks, available_hours_per_day=8)
    assert len(warnings) == 1
    assert "Warning" in warnings[0]

def test_no_conflict_far_future():
    # 10h task due in 30 days — plenty of time, no warning expected.
    task = make_task("T1", days=30, duration=10, level="medium")
    warnings = detect_conflicts([task], available_hours_per_day=8)
    assert warnings == []
