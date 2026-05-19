# Phase 4 Changes — How It Was Done
**COSC 499 -- Almas Waseem**

---

## 1. Conflict Detection Fix (algorithm.py)

The original `detect_conflicts` function compared the total hours of tasks due on the same day against a flat 8-hour limit. This caused a false warning for any task over 8 hours even if the deadline was weeks away.

The fix was to calculate how many working days exist between today and the deadline, then multiply by 8 to get the real available hours:

```python
days_available = max(1, (deadline_date - today).days)
available_hours = days_available * 8
```

Before the fix: a 10-hour task due in 30 days would warn because 10 > 8.
After the fix: a 10-hour task due in 30 days has 30 x 8 = 240 hours available, so no warning. A 10-hour task due tomorrow has 1 x 8 = 8 hours available, so the warning correctly fires.

---

## 2. GUI Redesign (gui/app.py)

The interface was restyled using `ttk.Style` with the `clam` theme as a base. A color palette was defined at the top of `app.py` and used consistently across all elements:

- Background: soft lavender `#f3f0fb`
- Header bar: deep purple `#6a1b9a`
- Add Task button: vivid purple `#7b2ff7`
- Mark Complete button: blue `#1976d2`
- Delete button: pink `#e91e8c`

The task table rows are color-coded by priority using Treeview tags. Each tag applies a background color to the whole row:

- High priority: pink `#fce4f7`
- Medium priority: lavender `#ede7f6`
- Low priority: light blue `#e3f2fd`
- Overdue: red `#ffcdd2`

A small color legend is displayed below the table so users know what each color means.

---

## 3. Task Editing

A double-click event was bound to the Treeview widget so that double-clicking any active row opens an edit dialog:

```python
self.tree.bind("<Double-1>", self._on_double_click)
```

The dialog is a `Toplevel` window that sits on top of the main window. `grab_set()` makes it modal so the user cannot interact with the main window until the dialog is closed. It is pre-filled with the selected task's current values. On save, the same validation as the add form runs. If it passes, `update_task` is called and the score is reset to 0 so it recalculates correctly on the next refresh. Completed tasks cannot be edited.

---

## 4. Overdue Indicator

Each time the table refreshes, every active task's deadline is compared against today's date:

```python
is_overdue = task.deadline.date() < datetime.now().date()
```

If overdue, the task gets the `"overdue"` Treeview tag instead of its priority tag, which applies the red background and red text. The status column shows `"Overdue"` instead of `"Active"`. The task stays in the ranked table and is not hidden.

---

## 5. Today's Plan Panel

A new panel was added between the task table and the add form, split into two side-by-side columns using a grid layout inside a `ttk.LabelFrame`.

### Left column — Today's Tasks

Tasks are split into three groups each refresh: overdue, due today, and future. Tasks due today are always included regardless of hours since they cannot be moved to another day. After accounting for their hours, the remaining time up to 8 hours is filled with the highest-priority future tasks:

```python
hours_used = sum(t.duration for t in due_today)
remaining  = max(0.0, 8.0 - hours_used)
upcoming   = due_today + build_today_plan(future, available_hours=remaining)
```

`build_today_plan` loops through future tasks in priority order and adds each one if it fits within the remaining hours.

### Right column — Overdue

All tasks whose deadline has already passed are listed here in red. The header shows the count, e.g. `"Overdue — 3 task(s)"`.

Both columns use read-only `tk.Text` widgets with colored text tags per line. `state=tk.DISABLED` prevents the user from typing in them. Both refresh automatically on every add, edit, complete, or delete.
