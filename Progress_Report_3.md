# Progress Report 3
**COSC 499 -- Intelligent Task Scheduling System**
**Student:** Almas Waseem
**Report Period:** Week 9-11 (March 8-27, 2026)

---

## What I Worked On

Since the last report, I completed Phase 2 and built out the graphical interface for Phase 3.

Phase 2 added a task manager layer on top of the scheduling algorithm. This is a separate file (`manager.py`) that handles adding, updating, completing, and deleting tasks by ID. Each operation raises an error if the task is not found, and updating any field on a task resets its score so it gets recalculated fresh the next time the schedule runs. I also wrote a second round of unit tests (`test_manager.py`) covering edge cases like empty task lists, all tasks being completed, partial field updates leaving other fields unchanged, and complex scenarios where marking a task complete resolves a previously detected conflict.

Phase 3 is the graphical interface, built using Python's Tkinter library. The main window displays a ranked task table showing each task's name, deadline, estimated hours, priority level, and computed score. Active tasks are sorted highest score first, and completed tasks appear grayed out at the bottom. Below the table, a red warning label appears automatically if any scheduling conflict is detected. A form at the bottom lets users add new tasks by entering a name, deadline, duration, and priority level. There are also buttons to mark a selected task as complete or delete it. The app validates all inputs before accepting them, including rejecting any deadline that falls in the past by comparing against the real current date at the time of submission. Tasks are saved to a JSON file automatically on every change and reloaded when the app is opened.

## Where Things Stand

The project is on schedule. Phases 1, 2, and 3 are complete. The next step is Phase 4, which focuses on polishing the interface, additional testing with realistic task scenarios, and code cleanup before the final submission.
