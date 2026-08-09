# Employee Leave Management Portal

## Project Purpose

This is a deliberately simple Flask web application used to teach **CI/CD
concepts using Jenkins**. It's a demo project for working professionals —
the focus is not on building a feature-complete HR system, but on having a
small, easy-to-explain codebase that can flow through a real CI/CD pipeline
(Git → GitHub → Jenkins → Build → Test → Deploy).

This repository is application-only. Jenkins, Docker, and deployment
configuration are **not** part of this project yet — they get layered on
top in a later step.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask |
| Database | SQLite |
| Frontend | HTML, CSS (Bootstrap 5), minimal JavaScript |
| Testing | pytest |
| Package management | pip, requirements.txt |

---

## Project Structure

```text
EmployeeLeavePortal/
├── app.py                     # Flask app: routes + SQLite setup
├── requirements.txt           # Python dependencies
├── templates/                 # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── employees.html
│   ├── add_employee.html
│   ├── leave_requests.html
│   └── apply_leave.html
├── static/
│   ├── css/
│   │   └── style.css          # Custom styling on top of Bootstrap 5
│   └── js/
│       └── script.js          # Minimal client-side date validation
├── tests/
│   └── test_app.py            # pytest test cases
├── README.md
└── .gitignore
```

`leave_portal.db` is created automatically the first time the app runs — it
is not committed to Git (see `.gitignore`).

---

## Pages

1. **Dashboard** – Total Employees, Total Leave Requests, Pending Requests,
   and Approved Requests, plus a Recent Leave Requests table
2. **Employees** – table of all employees, with an "Add Employee" form
   (Name, Department, Email, Leave Balance)
3. **Leave Requests** – table of all leave requests, with an "Apply for
   Leave" form (Employee, Leave Type, From Date, To Date, Reason) and
   simple Approve / Reject actions on pending requests

## Starter Data

On first run, the database is seeded with 5 employees and 5 leave requests
(a mix of Pending, Approved, and Rejected) so the Dashboard and tables
aren't empty the first time you open the app.

---

## How to Install

```bash
# 1. (Optional but recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

## How to Run

```bash
python app.py
```

The app runs at **http://127.0.0.1:5000** by default.

## How to Run Tests

```bash
pytest
```

This runs the test cases in `tests/test_app.py`, which check that the
application and dashboard load correctly, that a new employee can be added,
that a new leave request can be created, and that a pending request can be
approved. These are the same tests a Jenkins "Test" stage will run later.

---

## What's Intentionally Left Out (for now)

- No authentication or user accounts
- No REST API layer
- No frontend framework (React/Angular/Vue)
- No Docker
- No Jenkinsfile or Jenkins configuration

These are left out on purpose so the focus stays on the CI/CD pipeline
mechanics rather than application complexity. They can be added in a later
phase once the Jenkins pipeline itself is working end-to-end.
