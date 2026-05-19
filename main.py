"""Entry point for the Intelligent Task Scheduling System."""

from datetime import datetime, timedelta
from scheduler.task import Task
from scheduler.manager import (
    add_task,
    update_task,
    complete_task,
    delete_task,
    get_schedule,
    save,
    load,
)


def print_schedule(schedule: list[Task], warnings: list[str]) -> None:
    if not schedule:
        print("  (no active tasks)")
        return
    for rank, task in enumerate(schedule, start=1):
        print(f"  {rank}. {task}")
    if warnings:
        print("\n  Conflict Warnings:")
        for w in warnings:
            print(f"    {w}")
    else:
        print("\n  No scheduling conflicts detected.")


def demo() -> None:
    now = datetime.now()
    tasks: list[Task] = []

    print("=" * 60)
    print("  INTELLIGENT TASK SCHEDULER - Phase 2 Demo")
    print("=" * 60)

    # --- Add tasks ---
    print("\n[1] Adding tasks...")
    add_task(tasks, Task("Write literature review", now + timedelta(days=2), 3.0, "high"))
    add_task(tasks, Task("Submit assignment 3",    now + timedelta(days=1), 2.0, "medium"))
    add_task(tasks, Task("Read chapter 7",          now + timedelta(days=10), 1.5, "low"))
    add_task(tasks, Task("Group project notes",     now + timedelta(days=1), 5.0, "high"))
    add_task(tasks, Task("Review lecture slides",   now + timedelta(days=20), 1.0, "low"))

    schedule, warnings = get_schedule(tasks)
    print(f"  Added {len(tasks)} tasks. Current schedule:")
    print_schedule(schedule, warnings)

    # --- Update a task ---
    print("\n[2] Updating 'Read chapter 7' deadline to 3 days out and priority to 'high'...")
    chapter_id = tasks[2].id
    update_task(tasks, chapter_id, deadline=now + timedelta(days=3), priority_level="high")
    schedule, warnings = get_schedule(tasks)
    print("  Schedule after update:")
    print_schedule(schedule, warnings)

    # --- Complete a task ---
    print("\n[3] Marking 'Submit assignment 3' as completed...")
    assignment_id = tasks[1].id
    complete_task(tasks, assignment_id)
    schedule, warnings = get_schedule(tasks)
    print("  Schedule after completion:")
    print_schedule(schedule, warnings)

    # --- Delete a task ---
    print("\n[4] Deleting 'Review lecture slides'...")
    slides_id = tasks[4].id
    delete_task(tasks, slides_id)
    schedule, warnings = get_schedule(tasks)
    print("  Schedule after deletion:")
    print_schedule(schedule, warnings)

    # --- Conflict scenario ---
    print("\n[5] Adding tasks to trigger a scheduling conflict...")
    add_task(tasks, Task("Big assignment",  now + timedelta(days=1), 4.0, "high"))
    add_task(tasks, Task("Extra lab report", now + timedelta(days=1), 3.0, "medium"))
    schedule, warnings = get_schedule(tasks)
    print("  Schedule with conflict:")
    print_schedule(schedule, warnings)

    # --- Save and reload ---
    print("\n[6] Saving and reloading from disk...")
    save(tasks)
    reloaded = load()
    print(f"  Saved {len(tasks)} tasks, reloaded {len(reloaded)} tasks.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    from gui.app import main
    main()
