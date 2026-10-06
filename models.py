from datetime import date, datetime


class Person:
    def __init__(self, name):
        self.name = name

    def describe(self):
        return self.name


class Patient:
    def __init__(self, patient_id, name, phone):
        self.patient_id = patient_id
        self.name = name
        self._phone = phone              # encapsulation: private attribute

    @property
    def phone(self):
        return self._phone


class Appointment:
    def __init__(self, patient_id, scheduled_date, status):
        self.patient_id = patient_id
        self.scheduled_date = datetime.strptime(scheduled_date, "%Y-%m-%d").date()
        self.status = status

    def days_overdue(self):
        if self.status == "Missed" and self.scheduled_date < date.today():
            return (date.today() - self.scheduled_date).days
        return 0

    def is_overdue(self):
        return self.days_overdue() > 0


class CareTeamMember(Person):            # inheritance
    def __init__(self, staff_id, name, role):
        super().__init__(name)
        self.staff_id = staff_id
        self.role = role
        self.assigned = []

    def describe(self):                  # polymorphism: overrides Person.describe
        return f"{self.name} ({self.role})"

    def assign(self, patient_id):
        if patient_id not in self.assigned:
            self.assigned.append(patient_id)


if __name__ == "__main__":
    a = Appointment("P001", "2026-09-20", "Missed")
    print(a.days_overdue(), a.is_overdue())
    print(CareTeamMember("S01", "Nisha", "Coordinator").describe())