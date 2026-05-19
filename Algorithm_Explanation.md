# How the Scheduling Algorithm Works
**COSC 499 — Intelligent Task Scheduling System**
**Student:** Almas Waseem

---

## Overview

The user inputs a task with four things:
- Task name
- Deadline
- Estimated duration (hours)
- Priority level (low / medium / high)

The system then automatically scores, ranks, and schedules all tasks. Here's exactly how.

---

## Step 1 — Task is Created

When a task is created, Python automatically assigns it a UUID — a randomly generated unique ID. This ensures two tasks with the same name can still be told apart.

```
ID:    f47ac10b-58cc-4372-a567-0e02b2c3d479
Name:  Write literature review
```

Every task also starts with `score = 0` and `completed = False` until the algorithm runs.

---

## Step 2 — Urgency Score (0–100)

Urgency is calculated purely based on how many days are left until the deadline.

**Formula:**
```
urgency = (1 - days_remaining / 30) × 100
```

| Days Left | Urgency Score |
|-----------|--------------|
| 0 or overdue | 100 |
| 5 days | ~83 |
| 15 days | ~50 |
| 25 days | ~17 |
| 30+ days | 0 |

The scale caps at 30 days — anything beyond that gets urgency = 0. Anything overdue gets urgency = 100.

**Example — task due in 20 days:**
```
urgency = (1 - 20/30) × 100
urgency = (1 - 0.667) × 100
urgency = 0.333 × 100
urgency = 33.3
```

---

## Step 3 — Importance Score (0–100)

Importance is set by the user when they create the task. The system maps their choice to a number:

| Priority | Value |
|----------|-------|
| Low      |    33 |
| Medium   |    66 |
| High     |   100 |

These values are evenly spaced across 0–100 so each level is equal distance apart. This also keeps importance on the same scale as urgency so both are comparable when blended.



**Example — priority set to high:**
```
importance = 100
```

**Example — priority set to medium:**
```
importance = 66
```

---

## Step 4 — Final Score (Blend)

The two scores are combined using weighted averaging. Urgency is weighted more (60%) because a task due tomorrow should rank high regardless of how important the user thinks it is.

**Formula:**
```
score = (urgency × 0.6) + (importance × 0.4)
```

**Example — due in 20 days, high priority:**
```
score = (33.3 × 0.6) + (100 × 0.4)
score = 19.98 + 40.0
score = 59.98 ≈ 60
```

**Same task but medium priority instead:**
```
score = (33.3 × 0.6) + (66 × 0.4)
score = 19.98 + 26.4
score = 46.38 ≈ 46
```

Same deadline, lower importance — score drops by ~14 points.

---

## Step 5 — Build the Schedule

1. Any task marked `completed = True` is filtered out
2. The algorithm scores every remaining task using the formula above
3. Tasks are sorted highest score → lowest

**Example with 3 tasks:**

| Task | Days Left | Priority | Urgency | Importance | Score |
|------|-----------|----------|---------|------------|-------|
| Submit assignment 3 | 2 | medium | 93.3 | 66 | 82.4 |
| Write literature review | 20 | high | 33.3 | 100 | 60.0 |
| Read chapter 7 | 25 | low | 16.7 | 33 | 23.2 |

**Final schedule:**
```
1. Submit assignment 3     → 82.4
2. Write literature review → 60.0
3. Read chapter 7          → 23.2
```

Assignment 3 goes first — it's more urgent even though it's only medium priority.

---

## Step 6 — Conflict Detection

After sorting, the system groups tasks by their deadline date and adds up the total hours for that day. If any day exceeds 8 hours, a warning fires.

**Example — two tasks due same day:**
- Task A: 5 hours
- Task B: 4 hours
- Total: 9 hours → exceeds 8h limit

```
WARNING: 2026-02-21 has 9.0h of tasks but only 8h available.
```

The system doesn't auto-fix it — just warns the user so they can adjust.

---

## Step 7 — Save to JSON

All tasks are written to a JSON file after every change. When the app is reopened, tasks are reloaded from that file so nothing is lost between sessions.

---

## Summary Flow

```
User inputs task
      ↓
UUID assigned automatically
      ↓
Urgency score calculated (days left)
      ↓
Importance score mapped (low/medium/high)
      ↓
Final score = (urgency × 0.6) + (importance × 0.4)
      ↓
Completed tasks filtered out
      ↓
Remaining tasks sorted highest → lowest
      ↓
Conflict check (total hours per day vs 8h limit)
      ↓
Saved to JSON
```
