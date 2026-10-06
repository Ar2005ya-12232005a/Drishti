import csv
import os

from models import Appointment, CareTeamMember, Patient

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


class FollowUpTracker:
    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        self.patients = {}
        self.appointments = {}
        self.team = {}
        self.assignments = {}            # patient_id -> staff_id

    def _read_csv(self, filename, required=True):
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            if required:
                raise FileNotFoundError(f"Missing data file: {path}")
            return []
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def load(self):
        self.patients, self.appointments = {}, {}
        self.team, self.assignments = {}, {}
        try:
            for r in self._read_csv("patients.csv"):
                self.patients[r["patient_id"]] = Patient(
                    r["patient_id"], r["name"], r["phone"])
            for r in self._read_csv("followups.csv"):
                self.appointments[r["patient_id"]] = Appointment(
                    r["patient_id"], r["scheduled_date"], r["status"])
            for r in self._read_csv("team.csv"):
                self.team[r["staff_id"]] = CareTeamMember(
                    r["staff_id"], r["name"], r["role"])
            for r in self._read_csv("assignments.csv", required=False):
                pid, sid = r["patient_id"], r["staff_id"]
                if pid in self.patients and sid in self.team:
                    self.assignments[pid] = sid
                    self.team[sid].assign(pid)
        except KeyError as e:
            raise ValueError(f"A CSV file is missing the column {e}")
        return len(self.patients)

    def get_status(self, patient_id):
        patient_id = patient_id.strip().upper()
        if patient_id not in self.patients:
            raise KeyError(f"No patient with ID {patient_id}")
        p = self.patients[patient_id]
        a = self.appointments.get(patient_id)
        sid = self.assignments.get(patient_id)
        return {
            "id": p.patient_id,
            "name": p.name,
            "status": a.status if a else "No follow-up",
            "date": a.scheduled_date.isoformat() if a else "-",
            "overdue": a.days_overdue() if a else 0,
            "staff": self.team[sid].describe() if sid else "Unassigned",
        }

    def overdue_list(self):
        rows = [self.get_status(pid)
                for pid, a in self.appointments.items() if a.is_overdue()]
        return sorted(rows, key=lambda r: r["overdue"], reverse=True)

    def assign(self, patient_id, staff_id):
        if patient_id not in self.patients:
            raise KeyError(f"No patient with ID {patient_id}")
        if staff_id not in self.team:
            raise KeyError(f"No staff member with ID {staff_id}")
        old = self.assignments.get(patient_id)
        if old and patient_id in self.team[old].assigned:
            self.team[old].assigned.remove(patient_id)
        self.assignments[patient_id] = staff_id
        self.team[staff_id].assign(patient_id)
        self._save_assignments()

    def _save_assignments(self):
        path = os.path.join(self.data_dir, "assignments.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["patient_id", "staff_id"])
            w.writerows(self.assignments.items())

    def generate_report(self, path=None):
        path = path or os.path.join(BASE_DIR, "report.txt")
        rows = self.overdue_list()
        with open(path, "w", encoding="utf-8") as f:
            f.write("DRISHTI - Overdue Follow-Up Report\n")
            f.write("(Synthetic data. Administrative use only.)\n\n")
            f.write(f"Total overdue: {len(rows)}\n\n")
            for r in rows:
                f.write(f"{r['id']}  {r['name']:<25} {r['overdue']:>3} days  {r['staff']}\n")
        return path