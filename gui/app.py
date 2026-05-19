"""Main Tkinter application window for the Intelligent Task Scheduler."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from scheduler.task import Task
from scheduler.manager import add_task, update_task, complete_task, delete_task, get_schedule, save, load
from scheduler.algorithm import build_today_plan

FILEPATH = "tasks.json"

# ── Palette ────────────────────────────────────────────────────────────────
BG             = "#f3f0fb"
HEADER_BG      = "#6a1b9a"
HEADER_FG      = "#ffffff"
CARD_BG        = "#ffffff"
ACCENT         = "#7b2ff7"
ACCENT_DK      = "#5a00d6"
BTN_SUCCESS    = "#1976d2"
BTN_SUCCESS_DK = "#0d47a1"
BTN_DANGER     = "#e91e8c"
BTN_DANGER_DK  = "#c2185b"
ROW_HIGH       = "#fce4f7"
ROW_MED        = "#ede7f6"
ROW_LOW        = "#e3f2fd"
ROW_OVERDUE    = "#ffcdd2"
ROW_DONE       = "#f3f3f3"
TEXT_DONE      = "#aaaaaa"
TEXT_OVERDUE   = "#b71c1c"
WARN_FG        = "#c2185b"
HINT_FG        = "#b0a0c8"
TODAY_ACCENT   = "#4a148c"

FONT       = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SMALL = ("Segoe UI", 8)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Task Scheduler")
        self.geometry("1000x780")
        self.minsize(800, 700)
        self.configure(bg=BG)
        self.tasks: list[Task] = []
        self._apply_styles()
        self._build_ui()
        self._load()

    # ── Styles ───────────────────────────────────────────────────────────────

    def _apply_styles(self) -> None:
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure(".",              background=BG, font=FONT)
        s.configure("TFrame",         background=BG)
        s.configure("TLabel",         background=BG, font=FONT)
        s.configure("TLabelframe",    background=BG, relief="groove",
                    bordercolor="#d0d0d0")
        s.configure("TLabelframe.Label", background=BG, font=FONT_BOLD,
                    foreground=ACCENT)

        s.configure("Treeview",
            background=CARD_BG, fieldbackground=CARD_BG,
            font=FONT, rowheight=30,
        )
        s.configure("Treeview.Heading",
            background="#e8d5f5", foreground="#4a0080",
            font=FONT_BOLD, relief="flat",
        )
        s.map("Treeview",
            background=[("selected", "#d1b3f5")],
            foreground=[("selected", "#2d0060")],
        )
        s.map("Treeview.Heading", background=[("active", "#d1b3f5")])

        for name, bg, active in [
            ("Accent.TButton",  ACCENT,      ACCENT_DK),
            ("Success.TButton", BTN_SUCCESS, BTN_SUCCESS_DK),
            ("Danger.TButton",  BTN_DANGER,  BTN_DANGER_DK),
        ]:
            s.configure(name, background=bg, foreground="#ffffff",
                        font=FONT_BOLD, padding=(14, 7), relief="flat",
                        borderwidth=0)
            s.map(name, background=[("active", active), ("pressed", active)])

        s.configure("TEntry",    font=FONT, padding=5)
        s.configure("TCombobox", font=FONT, padding=5)
        s.configure("TScrollbar",
            background="#d0d0d0", troughcolor=BG,
            arrowcolor="#888888", relief="flat",
        )

    # ── UI build ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_header()
        self._build_table()
        self._build_warnings()
        self._build_today_panel()
        self._build_form()
        self._build_action_buttons()

    def _build_header(self) -> None:
        bar = tk.Frame(self, bg=HEADER_BG, pady=14)
        bar.pack(fill=tk.X)
        tk.Label(bar, text="Intelligent Task Scheduler",
                 bg=HEADER_BG, fg=HEADER_FG, font=FONT_TITLE).pack(
            side=tk.LEFT, padx=20)
        tk.Label(bar, text="Stay on top of what matters",
                 bg=HEADER_BG, fg="#b0bff8", font=("Segoe UI", 9)).pack(
            side=tk.LEFT)

    def _build_table(self) -> None:
        outer = ttk.Frame(self, padding=(12, 10, 12, 0))
        outer.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(outer, bg=CARD_BG, bd=1, relief="solid",
                        highlightbackground="#d8d8e8", highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        columns = ("rank", "name", "deadline", "duration", "priority", "score", "status")
        self.tree = ttk.Treeview(card, columns=columns, show="headings",
                                 selectmode="browse")

        col_cfg: dict[str, tuple[str, int, str]] = {
            "rank":     ("#",        45,  tk.CENTER),
            "name":     ("Task",    265,  tk.W),
            "deadline": ("Deadline",115,  tk.CENTER),
            "duration": ("Hours",    70,  tk.CENTER),
            "priority": ("Priority", 90,  tk.CENTER),
            "score":    ("Score",    75,  tk.CENTER),
            "status":   ("Status",   90,  tk.CENTER),
        }
        for col, (heading, width, anchor) in col_cfg.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=anchor, minwidth=40)

        self.tree.tag_configure("high",    background=ROW_HIGH)
        self.tree.tag_configure("medium",  background=ROW_MED)
        self.tree.tag_configure("low",     background=ROW_LOW)
        self.tree.tag_configure("overdue", background=ROW_OVERDUE,
                                foreground=TEXT_OVERDUE)
        self.tree.tag_configure("done",    background=ROW_DONE,
                                foreground=TEXT_DONE)

        self.tree.bind("<Double-1>", self._on_double_click)

        sb = ttk.Scrollbar(card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # legend
        legend = ttk.Frame(outer)
        legend.pack(anchor=tk.E, pady=(3, 0))
        for label, color in [("High", ROW_HIGH), ("Medium", ROW_MED),
                              ("Low", ROW_LOW), ("Overdue", ROW_OVERDUE)]:
            swatch = tk.Frame(legend, bg=color, width=12, height=12,
                              bd=1, relief="solid")
            swatch.pack(side=tk.LEFT, padx=(6, 2))
            tk.Label(legend, text=label, bg=BG,
                     font=FONT_SMALL, fg="#555555").pack(side=tk.LEFT)

    def _build_warnings(self) -> None:
        f = ttk.Frame(self, padding=(12, 3))
        f.pack(fill=tk.X)
        self.warnings_var = tk.StringVar()
        ttk.Label(f, textvariable=self.warnings_var,
                  foreground=WARN_FG, font=FONT_SMALL).pack(side=tk.LEFT)

    def _build_today_panel(self) -> None:
        outer = ttk.LabelFrame(self, text="  Today's Plan  ", padding=(12, 8))
        outer.pack(fill=tk.X, padx=12, pady=(2, 4))

        cols = ttk.Frame(outer)
        cols.pack(fill=tk.X)
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)

        # ── Left: Today's tasks ──────────────────────────────────────────────
        left = tk.Frame(cols, bg=CARD_BG, bd=1, relief="solid",
                        highlightbackground="#d1b3f5", highlightthickness=1)
        left.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))

        left_hdr = tk.Frame(left, bg="#ede7f6", pady=6)
        left_hdr.pack(fill=tk.X)
        self.today_header_var = tk.StringVar(value="Today's Tasks")
        tk.Label(left_hdr, textvariable=self.today_header_var,
                 bg="#ede7f6", fg=TODAY_ACCENT, font=FONT_BOLD).pack(
            side=tk.LEFT, padx=10)

        self.today_text = tk.Text(
            left, height=3, font=FONT, bg=CARD_BG,
            relief="flat", wrap=tk.WORD, state=tk.DISABLED, cursor="arrow",
        )
        self.today_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self.today_text.tag_configure("task",  foreground="#333333")
        self.today_text.tag_configure("empty", foreground=HINT_FG,
                                      font=("Segoe UI", 9, "italic"))

        # ── Right: Overdue ───────────────────────────────────────────────────
        right = tk.Frame(cols, bg=CARD_BG, bd=1, relief="solid",
                         highlightbackground="#ffcdd2", highlightthickness=1)
        right.grid(row=0, column=1, sticky=tk.NSEW, padx=(6, 0))

        right_hdr = tk.Frame(right, bg=ROW_OVERDUE, pady=6)
        right_hdr.pack(fill=tk.X)
        self.overdue_header_var = tk.StringVar(value="Overdue")
        tk.Label(right_hdr, textvariable=self.overdue_header_var,
                 bg=ROW_OVERDUE, fg=TEXT_OVERDUE, font=FONT_BOLD).pack(
            side=tk.LEFT, padx=10)

        self.overdue_text = tk.Text(
            right, height=3, font=FONT, bg=CARD_BG,
            relief="flat", wrap=tk.WORD, state=tk.DISABLED, cursor="arrow",
        )
        self.overdue_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self.overdue_text.tag_configure("overdue", foreground=TEXT_OVERDUE)
        self.overdue_text.tag_configure("empty",   foreground=HINT_FG,
                                        font=("Segoe UI", 9, "italic"))

    def _build_form(self) -> None:
        form = ttk.LabelFrame(self, text="  Add New Task  ", padding=(16, 10))
        form.pack(fill=tk.X, padx=12, pady=(0, 4))

        ttk.Label(form, text="Task name", font=FONT_BOLD).grid(
            row=0, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(form, text="Deadline", font=FONT_BOLD).grid(
            row=0, column=3, columnspan=2, sticky=tk.W, padx=(10, 0))
        ttk.Label(form, text="Duration (hrs)", font=FONT_BOLD).grid(
            row=0, column=6, columnspan=2, sticky=tk.W, padx=(10, 0))
        ttk.Label(form, text="Priority", font=FONT_BOLD).grid(
            row=0, column=9, columnspan=2, sticky=tk.W, padx=(10, 0))

        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(
            row=1, column=0, columnspan=2, sticky=tk.EW, pady=(3, 0))

        self.deadline_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.deadline_var, width=14).grid(
            row=1, column=3, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(3, 0))
        ttk.Label(form, text="YYYY-MM-DD", font=FONT_SMALL,
                  foreground=HINT_FG).grid(row=2, column=3, columnspan=2,
                                           sticky=tk.W, padx=(10, 0))

        self.duration_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.duration_var, width=8).grid(
            row=1, column=6, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(3, 0))
        ttk.Label(form, text="e.g. 1.5", font=FONT_SMALL,
                  foreground=HINT_FG).grid(row=2, column=6, columnspan=2,
                                           sticky=tk.W, padx=(10, 0))

        self.priority_var = tk.StringVar(value="medium")
        ttk.Combobox(form, textvariable=self.priority_var,
                     values=["low", "medium", "high"],
                     state="readonly", width=10).grid(
            row=1, column=9, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(3, 0))

        ttk.Button(form, text="+ Add Task", command=self._on_add,
                   style="Accent.TButton").grid(row=1, column=12,
                                                padx=(16, 0), pady=(3, 0))

    def _build_action_buttons(self) -> None:
        f = ttk.Frame(self, padding=(12, 4, 12, 10))
        f.pack(fill=tk.X)
        ttk.Button(f, text="Mark Complete", command=self._on_complete,
                   style="Success.TButton").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(f, text="Delete Task", command=self._on_delete,
                   style="Danger.TButton").pack(side=tk.LEFT)
        ttk.Label(f, text="Double-click a task to edit it",
                  font=FONT_SMALL, foreground=HINT_FG).pack(
            side=tk.RIGHT, padx=(0, 4))

    # ── Data helpers ─────────────────────────────────────────────────────────

    def _load(self) -> None:
        try:
            self.tasks = load(FILEPATH)
        except (FileNotFoundError, KeyError):
            self.tasks = []
        self._refresh()

    def _save(self) -> None:
        save(self.tasks, FILEPATH)

    def _refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        schedule, warnings = get_schedule(self.tasks)
        today = datetime.now().date()

        for rank, task in enumerate(schedule, start=1):
            is_overdue = task.deadline.date() < today
            tag = "overdue" if is_overdue else task.priority_level
            status = "Overdue" if is_overdue else "Active"
            self.tree.insert("", tk.END, iid=task.id, values=(
                rank,
                task.name,
                task.deadline.strftime("%Y-%m-%d"),
                f"{task.duration}h",
                task.priority_level.capitalize(),
                f"{task.score:.1f}",
                status,
            ), tags=(tag,))

        for task in self.tasks:
            if task.completed:
                self.tree.insert("", tk.END, iid=task.id, values=(
                    "—",
                    task.name,
                    task.deadline.strftime("%Y-%m-%d"),
                    f"{task.duration}h",
                    task.priority_level.capitalize(),
                    f"{task.score:.1f}",
                    "Done",
                ), tags=("done",))

        self.warnings_var.set("  ".join(warnings) if warnings else "")
        self._refresh_today_panel(schedule)

    def _refresh_today_panel(self, schedule: list[Task]) -> None:
        today    = datetime.now().date()
        overdue   = [t for t in schedule if t.deadline.date() < today]
        due_today = [t for t in schedule if t.deadline.date() == today]
        future    = [t for t in schedule if t.deadline.date() > today]
        # Always show tasks due today, then greedily fill remaining hours with future tasks
        hours_used = sum(t.duration for t in due_today)
        remaining  = max(0.0, 8.0 - hours_used)
        upcoming   = due_today + build_today_plan(future, available_hours=remaining)

        # ── Today's tasks column ─────────────────────────────────────────────
        self.today_text.configure(state=tk.NORMAL)
        self.today_text.delete("1.0", tk.END)
        if upcoming:
            planned = sum(t.duration for t in upcoming)
            self.today_header_var.set(f"Today's Tasks  —  {planned:.1f}h of 8.0h")
            for i, task in enumerate(upcoming, 1):
                self.today_text.insert(
                    tk.END,
                    f"{i}.  {task.name}  ({task.duration}h · {task.priority_level.capitalize()})\n",
                    "task",
                )
        else:
            self.today_header_var.set("Today's Tasks")
            self.today_text.insert(tk.END, "You're all clear for today!", "empty")
        self.today_text.configure(state=tk.DISABLED)

        # ── Overdue column ───────────────────────────────────────────────────
        self.overdue_text.configure(state=tk.NORMAL)
        self.overdue_text.delete("1.0", tk.END)
        if overdue:
            self.overdue_header_var.set(f"⚠  Overdue  —  {len(overdue)} task(s)")
            for task in overdue:
                self.overdue_text.insert(
                    tk.END,
                    f"•  {task.name}  ({task.duration}h · {task.priority_level.capitalize()})\n",
                    "overdue",
                )
        else:
            self.overdue_header_var.set("Overdue")
            self.overdue_text.insert(tk.END, "No overdue tasks.", "empty")
        self.overdue_text.configure(state=tk.DISABLED)

    def _selected_id(self) -> str | None:
        sel = self.tree.selection()
        return sel[0] if sel else None

    # ── Edit dialog ───────────────────────────────────────────────────────────

    def _on_double_click(self, event: tk.Event) -> None:
        task_id = self._selected_id()
        if not task_id:
            return
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task and not task.completed:
            self._open_edit_dialog(task)

    def _open_edit_dialog(self, task: Task) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Edit Task")
        dialog.configure(bg=BG)
        dialog.resizable(False, False)
        dialog.grab_set()  # modal

        # centre over main window
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 220) // 2
        dialog.geometry(f"400x220+{x}+{y}")

        ttk.Label(dialog, text="Edit Task", font=FONT_TITLE,
                  foreground=ACCENT).pack(pady=(16, 10))

        form = ttk.Frame(dialog, padding=(20, 0))
        form.pack(fill=tk.X)

        fields = [
            ("Task name",       0),
            ("Deadline",        1),
            ("Duration (hrs)",  2),
            ("Priority",        3),
        ]
        for text, row in fields:
            ttk.Label(form, text=text, font=FONT_BOLD).grid(
                row=row, column=0, sticky=tk.W, pady=3)

        name_var = tk.StringVar(value=task.name)
        ttk.Entry(form, textvariable=name_var, width=28).grid(
            row=0, column=1, sticky=tk.EW, padx=(10, 0))

        deadline_var = tk.StringVar(value=task.deadline.strftime("%Y-%m-%d"))
        ttk.Entry(form, textvariable=deadline_var, width=28).grid(
            row=1, column=1, sticky=tk.EW, padx=(10, 0))

        duration_var = tk.StringVar(value=str(task.duration))
        ttk.Entry(form, textvariable=duration_var, width=28).grid(
            row=2, column=1, sticky=tk.EW, padx=(10, 0))

        priority_var = tk.StringVar(value=task.priority_level)
        ttk.Combobox(form, textvariable=priority_var,
                     values=["low", "medium", "high"],
                     state="readonly", width=26).grid(
            row=3, column=1, sticky=tk.EW, padx=(10, 0))

        def _save() -> None:
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Missing field", "Task name is required.",
                                     parent=dialog)
                return
            try:
                deadline = datetime.strptime(deadline_var.get().strip(), "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid date",
                                     "Deadline must be YYYY-MM-DD (e.g. 2026-05-01).",
                                     parent=dialog)
                return
            try:
                duration = float(duration_var.get().strip())
                if duration <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid duration",
                                     "Duration must be a positive number.",
                                     parent=dialog)
                return

            update_task(self.tasks, task.id,
                        name=name, deadline=deadline,
                        duration=duration, priority_level=priority_var.get())
            self._save()
            self._refresh()
            dialog.destroy()

        btn_row = ttk.Frame(dialog, padding=(20, 8))
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Save Changes", command=_save,
                   style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="Cancel", command=dialog.destroy).pack(
            side=tk.LEFT)

    # ── Button handlers ───────────────────────────────────────────────────────

    def _on_add(self) -> None:
        name         = self.name_var.get().strip()
        deadline_str = self.deadline_var.get().strip()
        duration_str = self.duration_var.get().strip()
        priority     = self.priority_var.get()

        if not name:
            messagebox.showerror("Missing field", "Please enter a task name.")
            return
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date",
                                 "Deadline must be YYYY-MM-DD (e.g. 2026-05-01).")
            return
        if deadline.date() < datetime.now().date():
            messagebox.showerror("Invalid date", "Deadline can't be in the past.")
            return
        try:
            duration = float(duration_str)
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid duration",
                                 "Duration must be a positive number (e.g. 1.5).")
            return

        add_task(self.tasks, Task(name=name, deadline=deadline,
                                  duration=duration, priority_level=priority))
        self._save()
        self._refresh()
        self.name_var.set("")
        self.deadline_var.set("")
        self.duration_var.set("")
        self.priority_var.set("medium")

    def _on_complete(self) -> None:
        task_id = self._selected_id()
        if not task_id:
            messagebox.showwarning("Nothing selected",
                                   "Click a task in the list first.")
            return
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task and task.completed:
            messagebox.showinfo("Already done",
                                "That task is already marked complete.")
            return
        complete_task(self.tasks, task_id)
        self._save()
        self._refresh()

    def _on_delete(self) -> None:
        task_id = self._selected_id()
        if not task_id:
            messagebox.showwarning("Nothing selected",
                                   "Click a task in the list first.")
            return
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task and not messagebox.askyesno(
                "Delete task", f"Remove \"{task.name}\"? This can't be undone."):
            return
        delete_task(self.tasks, task_id)
        self._save()
        self._refresh()


def main() -> None:
    app = App()
    app.mainloop()
