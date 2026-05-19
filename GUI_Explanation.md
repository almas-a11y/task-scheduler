# GUI Explanation — gui/app.py
**COSC 499 | Intelligent Task Scheduling System**
**Student: Almas Waseem**

---

## What is Tkinter?

Tkinter is a library that comes built into Python by default. You do not install it separately or
log into anything. It is just available as part of Python. It lets you build real graphical
windows with buttons, text boxes, tables, and dropdowns using regular Python code.

There are two parts used in this project:
- `tkinter` (imported as `tk`) -- the base library for creating windows and widgets
- `tkinter.ttk` (imported as `ttk`) -- a styled version of the same widgets that looks cleaner

---

## The App Class (lines 13-195)

The entire GUI is built inside a class called `App`. This class extends `tk.Tk`, which means
it IS the window. When Python runs `App()`, the window appears on screen.

Inside `__init__` (the constructor), four things happen:
1. The window title and size are set (950x550 pixels)
2. An empty list is created to hold the tasks in memory
3. `_build_ui()` is called to draw all the widgets on screen
4. `_load()` is called to read saved tasks from disk and display them

---

## Building the UI -- _build_ui() (lines 23-88)

This function draws every visual element on the screen. It runs once when the app starts.

### The Task Table (lines 25-51)

The table is built using `ttk.Treeview`. A Treeview is a widget that displays data in rows
and columns, similar to a spreadsheet. The columns defined are: rank, name, deadline,
duration, priority, score, and status.

Each column is given a heading (the label shown at the top), a width in pixels, and an
alignment (left or center). The name column is left-aligned since it is text. The rest are
centered.

Completed tasks need to look different from active ones. This is handled by
`tag_configure("done", foreground="gray")` on line 46. Any row tagged as "done" will
automatically be displayed in gray text.

A scrollbar is also attached to the right side of the table so the user can scroll if there are
many tasks.

### The Conflict Warning Label (lines 53-57)

Below the table there is a label connected to a `StringVar` called `warnings_var`. A
`StringVar` is a special Tkinter variable that, when changed, automatically updates whatever
widget is connected to it. So when a conflict is detected, the code just sets `warnings_var`
to the warning text and the red label on screen updates by itself.

### The Add Task Form (lines 59-82)

The form sits inside a `LabelFrame`, which is a bordered box with a title. Inside it, the
following widgets are placed using `grid` layout:

- `Label` widgets -- the text that says "Name:", "Deadline:", etc.
- `Entry` widgets -- the text boxes the user types into
- `Combobox` -- the dropdown for selecting low, medium, or high priority
- A `Button` labeled "Add Task" that triggers `_on_add` when clicked

Each Entry and the Combobox are connected to their own `StringVar` so the code can read
the user's input later.

The form uses `grid` layout instead of `pack` because grid lets you place things in exact
row and column positions, which is needed to line up labels and inputs neatly side by side.

### The Action Buttons (lines 84-88)

Two buttons sit below the form: "Mark Complete" and "Delete Task". Both use `pack` layout
and are placed side by side. Each button is connected to a function that runs when clicked.

---

## Loading and Saving -- _load() and _save() (lines 92-100)

`_load()` runs once at startup. It tries to read tasks from `tasks.json`. If the file does not
exist yet (first time running the app), it just starts with an empty list. After loading, it
calls `_refresh()` to display the tasks.

`_save()` writes the current task list to `tasks.json`. It is called automatically every time
a task is added, completed, or deleted.

---

## Refreshing the Display -- _refresh() (lines 102-129)

This is the most important function in the GUI. Every time something changes, the whole
table is cleared and redrawn from scratch.

Here is what it does step by step:
1. Clears all existing rows from the Treeview
2. Calls `get_schedule()` from the manager layer, which rescores and sorts all active tasks
3. Inserts active tasks into the table in ranked order (rank 1 is highest priority)
4. Loops through all tasks again and inserts completed ones at the bottom with the "done"
   tag so they appear gray
5. Sets the warnings label text if any conflicts were detected, or clears it if not

This approach means the display is always accurate. There is no risk of the table showing
stale or out-of-order data.

---

## The Button Handlers

### Adding a Task -- _on_add() (lines 137-165)

When the user clicks "Add Task", this function runs. It reads the values from each form
field and validates them:

- Name cannot be empty
- Deadline must match the format YYYY-MM-DD (validated using `datetime.strptime`)
- Deadline cannot be in the past -- the app calls `datetime.now()` at the exact moment
  the button is clicked to get the real current date, then compares it against what the
  user typed. If the entered date is earlier than today, it rejects it with an error dialog.
- Duration must be a positive number (validated using `float()`)

If any validation fails, a `messagebox.showerror` dialog pops up explaining the problem and
the function stops. If everything is valid, a new Task object is created and passed to
`add_task()` from the manager layer. The app then saves and refreshes, and the form fields
are cleared back to their defaults.

### Marking Complete -- _on_complete() (lines 167-178)

This function checks if the user has selected a row in the table. If nothing is selected, a
warning dialog appears. If the selected task is already completed, an info dialog appears.
Otherwise, `complete_task()` is called from the manager layer, and the app saves and
refreshes.

### Deleting a Task -- _on_delete() (lines 180-190)

Same selection check as above. Before deleting, a confirmation dialog appears asking "Delete
'task name'?" so the user cannot accidentally remove a task. If confirmed, `delete_task()`
is called from the manager layer, and the app saves and refreshes.

---

## The main() Function (lines 193-195)

This is the entry point. It creates an instance of the App class (which opens the window)
and calls `mainloop()`. The `mainloop()` call keeps the window alive and listening for user
input until the window is closed.

---

## How the GUI Connects to the Rest of the App

The GUI does not contain any scheduling logic itself. It only imports from `scheduler/manager.py`
and calls its functions: `add_task`, `complete_task`, `delete_task`, `get_schedule`, `save`,
and `load`. The manager handles everything else. This separation means the algorithm can
be tested independently of the interface, and the interface can be changed without touching
the algorithm.