# Intelligent Task Scheduler

A desktop productivity app that automatically prioritizes your tasks using a custom scoring algorithm. Built with Python and Tkinter.

![App Screenshot](screenshots/app_screenshot.png)

---

## Features

- **Smart priority scoring** — every task gets a score from 0–100 based on urgency and importance
- **Conflict detection** — warns you when tasks due on the same day exceed your available hours
- **Today's Plan** — automatically builds a focused work list for the day (8h budget)
- **Overdue tracking** — overdue tasks are flagged and always surfaced first
- **Persistent storage** — tasks are saved to disk in JSON and reload on every launch
- **Edit in place** — double-click any task to update its name, deadline, duration, or priority
- **35 passing tests** — full pytest suite covering the algorithm and task manager

---

## Screenshots

| Main View | Pytest Suite |
|---|---|
| ![App](screenshots/app_screenshot.png) | ![Tests](screenshots/pytest_screenshot.png) |

---

## How the Algorithm Works

Each task gets a **priority score** computed as:

```
score = (urgency × 0.6) + (importance × 0.4)
```

**Urgency** (60%) is based on days remaining until the deadline, on a 0–30 day scale:

| Days Remaining | Urgency Score |
|---|---|
| Overdue | 100 |
| 1 day | ~96.7 |
| 5 days | ~83.3 |
| 15 days | ~50.0 |
| 30+ days | 0 |

**Importance** (40%) maps from the user's priority level:

| Priority | Score |
|---|---|
| High | 100 |
| Medium | 66 |
| Low | 33 |

Tasks are then sorted highest-to-lowest. Completed tasks are removed automatically. The full breakdown is in [ALGORITHM_EXPLAINED.md](ALGORITHM_EXPLAINED.md).

---

## Project Structure

```
task-scheduler/
├── scheduler/
│   ├── algorithm.py      # Priority scoring, schedule builder, conflict detection
│   ├── manager.py        # Add, update, complete, delete tasks
│   ├── storage.py        # JSON persistence (save/load)
│   └── task.py           # Task data model
├── gui/
│   ├── app.py            # Tkinter UI — main window, forms, event handlers
│   └── components/       # Reusable UI components
├── tests/
│   ├── test_algorithm.py # Unit tests for scoring and scheduling logic
│   └── test_manager.py   # Unit tests for task manager operations
├── main.py               # Entry point
└── requirements.txt
```

---

## Setup

**Requirements:** Python 3.11+

```bash
git clone https://github.com/YOUR_USERNAME/task-scheduler.git
cd task-scheduler
pip install -r requirements.txt
```

---

## Run

```bash
python main.py
```

---

## Run Tests

```bash
pytest tests/
```

Expected output: **35 passed**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| GUI | Tkinter (ttk) |
| Storage | JSON |
| Testing | pytest |
| Packaging | PyInstaller |
