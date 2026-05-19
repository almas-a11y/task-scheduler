# How the Scheduling Algorithm Works

## Overview
Every task gets a priority score from 0 to 100. The higher the score, the sooner you should work on it. The score is based on two things: how urgent the task is (deadline) and how important it is (priority level).

---

## The Formula

```
score = (urgency × 0.6) + (importance × 0.4)
```

Urgency makes up 60% of the score. Importance makes up 40%.

---

## Urgency (60% of score)

Urgency is based on how many days are left until the deadline, on a 0–30 day scale.

```
urgency = (1 - (days remaining / 30)) × 100
```

| Days Remaining | Urgency Score |
|---|---|
| 0 or less (overdue) | 100 |
| 1 day | ~96.7 |
| 5 days | ~83.3 |
| 15 days | ~50.0 |
| 29 days | ~3.3 |
| 30+ days | 0 |

Once a task is 30 or more days away, urgency drops to 0. Overdue tasks always get the maximum urgency of 100.

---

## Importance (40% of score)

Importance is mapped from the user's priority level:

| Priority Level | Importance Score |
|---|---|
| Low | 33 |
| Medium | 66 |
| High | 100 |

---

## Example Calculation

Task: due in 5 days, priority = high

```
urgency    = (1 - 5/30) × 100 = 83.3
importance = 100  (high)

score = (83.3 × 0.6) + (100 × 0.4)
      = 49.98 + 40.0
      = 89.98
```

Task: due in 5 days, priority = low

```
urgency    = 83.3
importance = 33  (low)

score = (83.3 × 0.6) + (33 × 0.4)
      = 49.98 + 13.2
      = 63.18
```

Same deadline, but the high priority task scores 89.98 vs 63.18 — it ranks higher.

---

## Scheduling Order

Once all tasks are scored, they are sorted highest to lowest. Completed tasks are removed from the list automatically. The result is the recommended order to work through your tasks.

---

## Conflict Detection

After scoring, the system checks if any day is overloaded. It adds up the total duration of all tasks due on the same day. If that total exceeds 8 hours, it throws a warning:

```
WARNING: 2026-03-07 has 12.0h of tasks but only 8.0h available.
```

This tells you that you have more work scheduled than realistically fits in a day.

---

## What Happens When You Update a Task

When you change a task's deadline or priority, the score is reset to 0. The next time `get_schedule()` is called, the formula runs again with the new values and the task gets a fresh score. This keeps the schedule always up to date.
