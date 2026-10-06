import threading
import tkinter as tk
from tkinter import messagebox, ttk

from client import DRISHTIClient
from tracker import FollowUpTracker


class DrishtiApp:
    def __init__(self, root):
        self.root = root
        root.title("DRISHTI - Follow-Up Visibility System")
        root.geometry("1050x700")
        self.tracker = FollowUpTracker()
        self.client = DRISHTIClient()
        self.loaded = False
        self.detail_vars = {}
        self.build_ui()

    # ---------------- layout ----------------
    def build_ui(self):
        tk.Label(self.root, text="DRISHTI", font=("Arial", 22, "bold"),
                 bg="#1f3b5c", fg="white", pady=8).pack(fill="x")

        # search frame (grid)
        search = tk.LabelFrame(self.root, text="Patient Search", padx=10, pady=8)
        search.pack(fill="x", padx=10, pady=5)
        tk.Label(search, text="Patient ID:").grid(row=0, column=0)
        self.entry = tk.Entry(search, width=15, font=("Arial", 12))
        self.entry.grid(row=0, column=1, padx=6)
        self.entry.bind("<Return>", lambda event: self.search())   # widget event
        tk.Button(search, text="Search", command=self.search).grid(row=0, column=2)

        # control frame (pack)
        ctrl = tk.LabelFrame(self.root, text="Controls", padx=10, pady=8)
        ctrl.pack(fill="x", padx=10, pady=5)
        tk.Button(ctrl, text="Load Records", command=self.load_records).pack(side="left", padx=4)
        tk.Button(ctrl, text="Check Overdue", command=self.check_overdue).pack(side="left", padx=4)
        self.staff_box = ttk.Combobox(ctrl, state="readonly", width=28)
        self.staff_box.pack(side="left", padx=4)
        tk.Button(ctrl, text="Assign Staff", command=self.assign_staff).pack(side="left", padx=4)
        tk.Button(ctrl, text="Generate Report", command=self.generate_report).pack(side="left", padx=4)

        # patient detail frame (grid)
        detail = tk.LabelFrame(self.root, text="Patient Details", padx=10, pady=8)
        detail.pack(fill="x", padx=10, pady=5)
        fields = [("ID", "id"), ("Name", "name"), ("Status", "status"),
                  ("Scheduled", "date"), ("Days overdue", "overdue"), ("Assigned to", "staff")]
        for i, (label, key) in enumerate(fields):
            row, col = i % 3, (i // 3) * 2
            tk.Label(detail, text=label + ":", font=("Arial", 10, "bold"),
                     width=13, anchor="w").grid(row=row, column=col, sticky="w")
            var = tk.StringVar(value="-")
            self.detail_vars[key] = var
            tk.Label(detail, textvariable=var, width=28, anchor="w").grid(row=row, column=col + 1, sticky="w")

        # server frame (pack)
        server = tk.LabelFrame(self.root, text="Server", padx=10, pady=8)
        server.pack(fill="x", padx=10, pady=5)
        tk.Button(server, text="Connect to Server", command=self.connect).pack(side="left", padx=4)
        tk.Button(server, text="Fetch HTML", command=self.fetch_html).pack(side="left", padx=4)
        tk.Button(server, text="Download HTML", command=self.download_html).pack(side="left", padx=4)
        self.conn_label = tk.Label(server, text="Not connected", fg="red")
        self.conn_label.pack(side="left", padx=10)

        self.status = tk.Label(self.root, text="Ready", anchor="w", relief="sunken")
        self.status.pack(fill="x", padx=10, pady=(5, 0))

        # results frame: overdue table + server response box
        res = tk.LabelFrame(self.root, text="Overdue Follow-ups  |  Server Response", padx=6, pady=6)
        res.pack(fill="both", expand=True, padx=10, pady=(5, 30))
        res.columnconfigure(0, weight=1)
        res.rowconfigure(0, weight=1)

        cols = ("id", "name", "status", "overdue", "staff")
        self.tree = ttk.Treeview(res, columns=cols, show="headings")
        for c, w in zip(cols, (70, 180, 80, 100, 180)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=w)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(res, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        self.html_box = tk.Text(res, width=42, wrap="word")
        self.html_box.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        # footer (place)
        tk.Label(self.root, fg="gray",
                 text="Synthetic data only. Administrative use, not medical advice."
                 ).place(relx=0.5, rely=1.0, anchor="s")

    # ---------------- helpers ----------------
    def set_status(self, text):
        self.status.config(text=text)

    def require_loaded(self):
        if not self.loaded:
            messagebox.showwarning("Not loaded", "Click 'Load Records' first.")
            return False
        return True

    def get_pid(self):
        pid = self.entry.get().strip().upper()
        if not pid:
            messagebox.showwarning("Input", "Enter a patient ID")
            return None
        return pid

    def show_details(self, info):
        for key, var in self.detail_vars.items():
            var.set(str(info[key]))

    # ---------------- local callbacks ----------------
    def load_records(self):
        try:
            count = self.tracker.load()
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Load error", str(e))
            return
        self.loaded = True
        self.staff_box["values"] = [f"{s.staff_id} - {s.describe()}"
                                    for s in self.tracker.team.values()]
        if self.staff_box["values"]:
            self.staff_box.current(0)
        self.set_status(f"Loaded {count} patients")
        messagebox.showinfo("Loaded", f"Loaded {count} patient records.")

    def search(self):
        if not self.require_loaded():
            return
        pid = self.get_pid()
        if not pid:
            return
        try:
            self.show_details(self.tracker.get_status(pid))
            self.set_status(f"Showing {pid}")
        except KeyError as e:
            messagebox.showerror("Not found", e.args[0])

    def check_overdue(self):
        if not self.require_loaded():
            return
        rows = self.tracker.overdue_list()
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end",
                             values=(r["id"], r["name"], r["status"], r["overdue"], r["staff"]))
        self.set_status(f"{len(rows)} overdue follow-ups")

    def assign_staff(self):
        if not self.require_loaded():
            return
        pid = self.get_pid()
        choice = self.staff_box.get()
        if not pid or not choice:
            return
        try:
            self.tracker.assign(pid, choice.split(" - ")[0])
        except KeyError as e:
            messagebox.showerror("Assign error", e.args[0])
            return
        self.show_details(self.tracker.get_status(pid))
        messagebox.showinfo("Assigned", f"{pid} assigned to {choice}")

    def generate_report(self):
        if not self.require_loaded():
            return
        try:
            path = self.tracker.generate_report()
        except OSError as e:
            messagebox.showerror("Report error", str(e))
            return
        messagebox.showinfo("Report saved", path)

    # ---------------- threaded network callbacks ----------------
    def run_in_thread(self, func, on_done):
        """Run func in a worker thread; deliver the result on the GUI thread."""
        def worker():
            try:
                result = func()
            except Exception as e:
                self.root.after(0, lambda err=e: self.on_error(err))
            else:
                self.root.after(0, lambda r=result: on_done(r))
        threading.Thread(target=worker, daemon=True).start()

    def on_error(self, err):
        self.set_status("Error")
        messagebox.showerror("Error", str(err))

    def connect(self):
        self.set_status("Connecting...")
        self.run_in_thread(self.client.ping, self.on_connected)

    def on_connected(self, _):
        self.conn_label.config(text="Connected", fg="green")
        self.set_status("Connected to server")

    def fetch_html(self):
        pid = self.get_pid()
        if not pid:
            return
        self.set_status(f"Fetching {pid}...")
        self.run_in_thread(lambda: self.client.fetch(pid), self.on_fetched)

    def on_fetched(self, html_text):
        self.html_box.delete("1.0", "end")
        self.html_box.insert("1.0", html_text)
        self.set_status("HTML received")

    def download_html(self):
        pid = self.get_pid()
        if not pid:
            return
        self.set_status(f"Downloading {pid}...")

        def job():
            return self.client.save_html(self.client.fetch(pid), pid)

        self.run_in_thread(job, self.on_downloaded)

    def on_downloaded(self, path):
        self.set_status("Download complete")
        messagebox.showinfo("Saved", f"Page saved to:\n{path}")


if __name__ == "__main__":
    root = tk.Tk()
    DrishtiApp(root)
    root.mainloop()