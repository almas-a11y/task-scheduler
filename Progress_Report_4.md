# Progress Report 4
**COSC 499 -- Intelligent Task Scheduling System**
**Student:** Almas Waseem
**Report Period:** Week 15-16 (April 1–10, 2026)

---

## What I Worked On;

This report covers Phase 4, which focused on fixing a logic bug, adding three new features, and improving the overall look and usability of the application.

The first change was a fix to the conflict detection algorithm in `algorithm.py`. The original implementation compared a task's total hours against a flat 8-hour daily limit, which caused tasks due far in the future to incorrectly trigger warnings. For example, a 10-hour task due in 30 days would warn even though 240 hours of working time were available. The fix was to multiply the number of days between today and the deadline by 8 to get the total available hours, using `max(1, (deadline_date - today).days)` so that same-day tasks always have at least one day's worth of time. Tasks that are genuinely overloaded relative to their deadline still trigger warnings correctly.

The interface was then fully redesigned. The application now uses a purple, blue, and pink color scheme applied through `ttk.Style` with the `clam` theme as a base. The header bar is deep purple, the Add button is vivid purple, Mark Complete is blue, and Delete is pink. Task table rows are color-coded by priority level, pink for high, lavender for medium, and light blue for low, with red used for overdue tasks. A color legend is displayed below the table for reference.

Three features were added on top of the redesign. The first is task editing. Previously there was no way to correct a task once it was added. A double-click event was bound to the task table that opens a `Toplevel` modal dialog pre-filled with the selected task's current values. On save, the same validation as the add form runs and `update_task` is called, which resets the score so it recalculates on the next schedule refresh. The second feature is an overdue indicator. Each time the table refreshes, tasks whose deadline has passed are detected by comparing `task.deadline.date()` against today's date. These receive a red row background and display "Overdue" in the status column instead of "Active". The third feature is a Today's Plan panel added between the task table and the add form. It is split into two side-by-side columns. The left column shows tasks for today. Anything due today is always included regardless of duration since it cannot be deferred, and the remaining hours up to 8 are filled greedily with the highest-priority future tasks. The right column lists all overdue tasks separately. Both columns use read-only `tk.Text` widgets with colored tags and update automatically whenever the task list changes.

## Where Things Stand

Phase 4 is complete. All 35 unit tests pass. The next step is Phase 5, which covers writing the final paper and preparing the project for submission.
