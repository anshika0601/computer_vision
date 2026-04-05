from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .attendance import run_attendance
from .database import fetch_attendance_rows, fetch_summary, init_database
from .registration import capture_face_samples
from .storage import rebuild_encodings


class FaceAttendanceApp:
    def __init__(self) -> None:
        init_database()
        self.root = tk.Tk()
        self.root.title("Face Attendance Dashboard")
        self.root.geometry("980x640")
        self.root.configure(bg="#f4efe6")

        self.name_var = tk.StringVar()
        self.samples_var = tk.IntVar(value=5)
        self.camera_index_var = tk.IntVar(value=0)
        self.tolerance_var = tk.DoubleVar(value=0.5)
        self.status_var = tk.StringVar(value="Ready.")
        self.summary_vars = {
            "people_count": tk.StringVar(value="0"),
            "attendance_count": tk.StringVar(value="0"),
            "today_count": tk.StringVar(value="0"),
        }

        self._build_layout()
        self.refresh_dashboard()

    def _build_layout(self) -> None:
        title = tk.Label(
            self.root,
            text="Face Attendance Recognition",
            font=("Segoe UI", 22, "bold"),
            bg="#f4efe6",
            fg="#1f3b4d",
        )
        title.pack(pady=(18, 8))

        subtitle = tk.Label(
            self.root,
            text="Register people, rebuild encodings, mark attendance, and review records.",
            font=("Segoe UI", 11),
            bg="#f4efe6",
            fg="#5b6b73",
        )
        subtitle.pack(pady=(0, 18))

        content = tk.Frame(self.root, bg="#f4efe6")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        self._build_controls(content)
        self._build_dashboard(content)

        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            font=("Segoe UI", 10),
            bg="#1f3b4d",
            fg="white",
            padx=12,
            pady=10,
        )
        status_bar.pack(fill="x", side="bottom")

    def _build_controls(self, parent: tk.Widget) -> None:
        controls = tk.Frame(parent, bg="white", bd=0, highlightthickness=1, highlightbackground="#d8cfc1")
        controls.grid(row=0, column=0, sticky="ns", padx=(0, 18))

        inner = tk.Frame(controls, bg="white", padx=18, pady=18)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="Controls", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f3b4d").pack(anchor="w")

        self._labeled_entry(inner, "Person name", self.name_var)
        self._labeled_entry(inner, "Samples", self.samples_var)
        self._labeled_entry(inner, "Camera index", self.camera_index_var)
        self._labeled_entry(inner, "Tolerance", self.tolerance_var)

        actions = [
            ("Register Face", self.start_register),
            ("Rebuild Encodings", self.start_rebuild),
            ("Start Attendance", self.start_attendance),
            ("Refresh Dashboard", self.refresh_dashboard),
        ]

        for label, command in actions:
            tk.Button(
                inner,
                text=label,
                command=command,
                font=("Segoe UI", 11, "bold"),
                bg="#d97706",
                fg="white",
                activebackground="#b45309",
                activeforeground="white",
                relief="flat",
                padx=12,
                pady=10,
                cursor="hand2",
            ).pack(fill="x", pady=6)

        help_text = (
            "Registration opens the webcam.\n"
            "Press 's' to save each face sample.\n"
            "Press 'q' to close webcam windows."
        )
        tk.Label(inner, text=help_text, justify="left", font=("Segoe UI", 10), bg="white", fg="#5b6b73").pack(
            anchor="w", pady=(12, 0)
        )

    def _build_dashboard(self, parent: tk.Widget) -> None:
        frame = tk.Frame(parent, bg="#f4efe6")
        frame.grid(row=0, column=1, sticky="nsew")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        stats = tk.Frame(frame, bg="#f4efe6")
        stats.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        stats.columnconfigure((0, 1, 2), weight=1)

        cards = [
            ("Registered People", "people_count"),
            ("Total Attendance", "attendance_count"),
            ("Today Marked", "today_count"),
        ]
        for index, (label, key) in enumerate(cards):
            card = tk.Frame(stats, bg="#1f3b4d", padx=18, pady=16)
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 10, 0))
            tk.Label(card, text=label, font=("Segoe UI", 11), bg="#1f3b4d", fg="#d6e2ea").pack(anchor="w")
            tk.Label(
                card,
                textvariable=self.summary_vars[key],
                font=("Segoe UI", 24, "bold"),
                bg="#1f3b4d",
                fg="white",
            ).pack(anchor="w", pady=(8, 0))

        table_shell = tk.Frame(frame, bg="white", highlightthickness=1, highlightbackground="#d8cfc1")
        table_shell.grid(row=1, column=0, sticky="nsew")
        table_shell.rowconfigure(0, weight=1)
        table_shell.columnconfigure(0, weight=1)

        columns = ("person_name", "attendance_date", "attendance_time", "status")
        self.tree = ttk.Treeview(table_shell, columns=columns, show="headings", height=18)
        headings = {
            "person_name": "Name",
            "attendance_date": "Date",
            "attendance_time": "Time",
            "status": "Status",
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, anchor="center", width=140)

        scrollbar = ttk.Scrollbar(table_shell, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _labeled_entry(self, parent: tk.Widget, label: str, variable: tk.Variable) -> None:
        tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"), bg="white", fg="#374151").pack(
            anchor="w", pady=(14, 4)
        )
        tk.Entry(parent, textvariable=variable, font=("Segoe UI", 11), relief="solid", bd=1).pack(fill="x")

    def _run_task(self, label: str, func, on_success=None) -> None:
        self.status_var.set(label)

        def worker() -> None:
            try:
                result = func()
            except Exception as exc:  # noqa: BLE001
                self.root.after(0, lambda: self._show_error(str(exc)))
                return

            def complete() -> None:
                if on_success is not None:
                    on_success(result)
                self.refresh_dashboard()

            self.root.after(0, complete)

        threading.Thread(target=worker, daemon=True).start()

    def _show_error(self, message: str) -> None:
        self.status_var.set("Action failed.")
        messagebox.showerror("Face Attendance", message)

    def start_register(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Face Attendance", "Enter a person name first.")
            return

        samples = int(self.samples_var.get())
        camera_index = int(self.camera_index_var.get())
        self._run_task(
            label=f"Registering {name}...",
            func=lambda: capture_face_samples(name=name, samples=samples, camera_index=camera_index),
            on_success=lambda _result: self.status_var.set(f"Finished registering {name}."),
        )

    def start_rebuild(self) -> None:
        self._run_task(
            label="Rebuilding encodings...",
            func=rebuild_encodings,
            on_success=lambda result: self.status_var.set(f"Saved {result} encoding(s)."),
        )

    def start_attendance(self) -> None:
        camera_index = int(self.camera_index_var.get())
        tolerance = float(self.tolerance_var.get())
        self._run_task(
            label="Attendance camera running...",
            func=lambda: run_attendance(camera_index=camera_index, tolerance=tolerance),
            on_success=lambda _result: self.status_var.set("Attendance session closed."),
        )

    def refresh_dashboard(self) -> None:
        summary = fetch_summary()
        for key, value in summary.items():
            self.summary_vars[key].set(str(value))

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in fetch_attendance_rows():
            self.tree.insert(
                "",
                "end",
                values=(row["person_name"], row["attendance_date"], row["attendance_time"], row["status"]),
            )

        self.status_var.set("Dashboard refreshed.")

    def run(self) -> None:
        self.root.mainloop()


def launch_gui() -> None:
    app = FaceAttendanceApp()
    app.run()
