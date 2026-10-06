# DRISHTI

**GUI-Based Client-Server Follow-Up Visibility and Care-Team Management System**

DRISHTI (Sanskrit *drishti*, "sight") is a Python project that helps a care team see which follow-up appointments were missed, how many days overdue they are, and who is responsible for each one. It has a Tkinter desktop app, a small HTTP server, and a CGI web form.

> **Scope:** DRISHTI uses synthetic demo data only. It handles administrative scheduling information. It does not diagnose, recommend treatment, calculate clinical risk, or give medical advice.

## Features

- Desktop dashboard built with Tkinter: search, overdue table, patient details and staff assignment
- Overdue detection from CSV records, sorted by days late
- Care-team assignment, saved back to `data/assignments.csv`
- Text report of all overdue follow-ups
- Background threads for network calls, so the window never freezes
- Python client and server that exchange HTML pages over HTTP
- Download any patient's status page as an HTML file
- Browser form that queries the same records through a CGI script

## Project structure

```
Drishti/
├── gui.py            Tkinter desktop app (run this)
├── client.py         DRISHTIClient: ping, fetch page, save page
├── server.py         DRISHTIServer: HTTP server that returns HTML
├── tracker.py        FollowUpTracker: loads CSVs, finds overdue, reports
├── models.py         Person, Patient, Appointment, CareTeamMember
├── theme.py          Shared CSS and HTML builders for all web pages
├── form.html         Web landing page with the CGI search form
├── cgi-bin/
│   └── status.py     CGI script that handles the form
├── data/
│   ├── patients.csv
│   ├── followups.csv
│   ├── team.csv
│   └── assignments.csv   (created when you assign staff)
└── downloads/        (saved HTML pages appear here)
```

## Requirements

- Python 3.8 or newer
- Tkinter (included with Python on Windows and macOS; on Debian/Ubuntu run `sudo apt install python3-tk`)
- No third-party packages

## How to run

DRISHTI uses two separate servers, so you need up to three terminals, all opened in the `Drishti` folder.

**1. Client/server server (port 8000)**

```
python server.py
```

**2. CGI web form (port 8080)**

```
python -m http.server --cgi 8080 --bind 127.0.0.1
```

Then open <http://localhost:8080/form.html>.

**3. Desktop app**

```
python gui.py
```

## Using the desktop app

1. Click **Load Records**. Nothing else works until you do.
2. Type a patient ID such as `P001` and click **Search** (or press Enter).
3. Click **Check Overdue** to list every overdue follow-up.
4. Choose a staff member, enter a patient ID and click **Assign Staff**.
5. Click **Generate Report** to write `report.txt`.
6. Click **Connect to Server** (needs `server.py` running).
7. Click **Fetch HTML** to see the server's response, or **Download HTML** to save it in `downloads/`.

You can also open a status page directly: <http://localhost:8000/?pid=P001>

## Sample data

`patients.csv`

| patient_id | name | phone |
|---|---|---|
| P001 | Aarav | 9876543210 |
| P002 | Ananya | 9876543211 |
| P003 | Rohan | 9876543212 |

`followups.csv`

| patient_id | scheduled_date | status |
|---|---|---|
| P001 | 2026-09-20 | Missed |
| P002 | 2026-09-29 | Completed |
| P003 | 2026-09-15 | Missed |

A follow-up counts as overdue when its status is `Missed` and the scheduled date is in the past. Overdue days are counted from the scheduled date to today.

## Concepts demonstrated

| Topic | Where |
|---|---|
| GUI, Tkinter widgets, dialogs | `gui.py` (buttons, labels, entries, combobox, table, message boxes) |
| Event-driven programming | Button callbacks and the Enter-key binding in `gui.py` |
| Layouts and frames | `grid`, `pack` and `place` with `LabelFrame`s |
| Multithreading | `run_in_thread` in `gui.py`, results returned with `root.after` |
| Networks, client/server | `client.py` and `server.py` over HTTP |
| HTML generation and queries | `theme.py` pages, `/?pid=...` query string |
| Downloading pages | `save_html` in `client.py` |
| CGI programming and form | `form.html` and `cgi-bin/status.py` |
| OOP | Classes in `models.py`, `tracker.py`, `client.py`, `server.py` |
| File handling | CSV input, `report.txt` and saved HTML output |
| Exception handling | Missing files, bad columns, unknown IDs, connection errors |

OOP details: `Patient` uses a private `_phone` attribute with a property (encapsulation). `CareTeamMember` inherits from `Person` and overrides `describe()` (inheritance and polymorphism).

## Troubleshooting

| Problem | Fix |
|---|---|
| "Cannot reach the server" in the GUI | Start `server.py` first |
| Browser shows `ERR_ADDRESS_INVALID` at `[::]:8080` | Use `http://localhost:8080/form.html` instead |
| Form page is blank or 404 | Start the 8080 server from the `Drishti` root folder, and make sure `form.html` is saved |
| CGI result page is blank or errors | Run `python cgi-bin/status.py` in a terminal to see the traceback |
| "Missing data file" on Load Records | Check that `patients.csv`, `followups.csv` and `team.csv` are in `data/` |
| Styling looks old | Hard-refresh with Ctrl+F5 |

## Notes

- `python -m http.server --cgi` is deprecated in recent Python versions but works for a demo.
- Server and client both run on `localhost`, so the "remote" server is simulated on one machine.
- Generated files (`downloads/`, `report.txt`, `data/assignments.csv`) are listed in `.gitignore`.