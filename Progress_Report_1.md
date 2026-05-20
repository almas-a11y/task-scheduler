# Progress Report 1
**COSC 499 — Intelligent Task Scheduling System**
**Student:** Almas Waseem
**Report Period:** Week 5 and 6 (February 8–20, 2026)

---

## What I Worked On This Week

This week was focused on setting up the project structure and implementing the core scheduling logic. The codebase is split into two layers: `scheduler/` for all the business logic and `gui/` for the Tkinter interface later, keeping them independent so each can be developed and tested on its own.

The `Task` data model (`task.py`) uses Python's `dataclass` decorator and stores a task's name, deadline, duration, user-set priority level, completion status, and a computed score. UUIDs handle unique identification, and `to_dict()` / `from_dict()` methods allow tasks to be serialized for JSON storage.

The priority scoring algorithm (`algorithm.py`) is the core of the project. It scores each task from 0–100 using:
- **Urgency (60%):** Days left until the deadline on a 0–30 day scale. Overdue tasks get max urgency.
- **Importance (40%):** Mapped from the user's priority level — Low = 33, Medium = 66, High = 100.

Formula: `score = (urgency × 0.6) + (importance × 0.4)`

Completed tasks are excluded automatically. A conflict detection function also flags when tasks on the same deadline day exceed 8 hours of total work.

Storage is JSON-based (`storage.py`), and `main.py` serves as a CLI demo that runs the algorithm on sample tasks to verify output. Unit tests cover urgency edge cases, priority comparisons, sort order, and conflict detection.

## Where Things Stand

Everything planned for Week 5 and 6 is done. Week 7 will focus on algorithm edge cases (overdue tasks, identical scores), more tests, and starting to plan the GUI integration.
