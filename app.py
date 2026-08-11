"""
Employee Leave Management Portal
---------------------------------
A deliberately simple Flask application used to teach CI/CD concepts with
Jenkins. The business logic is kept minimal on purpose - the point of this
project is the pipeline (Git -> GitHub -> Jenkins -> Build -> Test -> Deploy),
not the application itself.

Run locally with:
    pip install -r requirements.txt
    python app.py
"""

import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

# A session secret key is required for flash messages to work. Fine for
# this teaching demo; a real app would load this from an environment
# variable instead of hardcoding it.
app.secret_key = "leave-portal-dev-secret-key"

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "leave_portal.db")

LEAVE_TYPES = ["Sick Leave", "Casual Leave", "Earned Leave"]


def get_db_connection():
    """Open a new SQLite connection. Rows behave like dictionaries."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the tables and seed a few starter rows (only once)."""
    conn = get_db_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            department    TEXT NOT NULL,
            email         TEXT NOT NULL,
            leave_balance INTEGER NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leave_requests (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type  TEXT NOT NULL,
            from_date   TEXT NOT NULL,
            to_date     TEXT NOT NULL,
            reason      TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'Pending',
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        """
    )
    conn.commit()

    # Only seed if empty, so restarting the app never duplicates starter data.
    employee_count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if employee_count == 0:
        starter_employees = [
            ("Aditi Sharma.", "Engineering", "aditi.sharma@company.com", 18),
            ("Rohan Verma", "Sales", "rohan.verma@company.com", 20),
            ("Priya Nair", "Human Resources", "priya.nair@company.com", 15),
            ("Karan Mehta", "Finance", "karan.mehta@company.com", 22),
            ("Sneha Iyer", "Engineering", "sneha.iyer@company.com", 19),
        ]
        conn.executemany(
            """INSERT INTO employees (name, department, email, leave_balance)
               VALUES (?, ?, ?, ?)""",
            starter_employees,
        )
        conn.commit()

        starter_requests = [
            (1, "Sick Leave", "2026-08-10", "2026-08-12", "Fever and rest", "Pending"),
            (2, "Casual Leave", "2026-08-15", "2026-08-16", "Personal work", "Approved"),
            (3, "Earned Leave", "2026-08-20", "2026-08-25", "Family vacation", "Pending"),
            (4, "Sick Leave", "2026-08-05", "2026-08-06", "Not feeling well", "Rejected"),
            (5, "Casual Leave", "2026-08-18", "2026-08-18", "Personal errand", "Approved"),
        ]
        conn.executemany(
            """INSERT INTO leave_requests
               (employee_id, leave_type, from_date, to_date, reason, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            starter_requests,
        )
        conn.commit()

    conn.close()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def dashboard():
    """Dashboard - headline numbers plus the 5 most recent leave requests."""
    conn = get_db_connection()

    total_employees = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    total_requests = conn.execute("SELECT COUNT(*) FROM leave_requests").fetchone()[0]
    pending_requests = conn.execute(
        "SELECT COUNT(*) FROM leave_requests WHERE status = 'Pending'"
    ).fetchone()[0]
    approved_requests = conn.execute(
        "SELECT COUNT(*) FROM leave_requests WHERE status = 'Approved'"
    ).fetchone()[0]

    recent_requests = conn.execute(
        """
        SELECT leave_requests.id,
               employees.name AS employee_name,
               leave_requests.leave_type,
               leave_requests.from_date,
               leave_requests.to_date,
               leave_requests.status
        FROM leave_requests
        JOIN employees ON employees.id = leave_requests.employee_id
        ORDER BY leave_requests.id DESC
        LIMIT 5
        """
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_employees=total_employees,
        total_requests=total_requests,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        recent_requests=recent_requests,
    )


@app.route("/employees")
def employees():
    """Employees - a simple table of everyone in the system."""
    conn = get_db_connection()
    all_employees = conn.execute("SELECT * FROM employees ORDER BY id").fetchall()
    conn.close()
    return render_template("employees.html", employees=all_employees)


@app.route("/employees/add", methods=["GET", "POST"])
def add_employee():
    """Add Employee - a small form that inserts one row."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        email = request.form.get("email", "").strip()
        leave_balance = request.form.get("leave_balance", "0")

        if name and department and email:
            conn = get_db_connection()
            conn.execute(
                """INSERT INTO employees (name, department, email, leave_balance)
                   VALUES (?, ?, ?, ?)""",
                (name, department, email, int(leave_balance)),
            )
            conn.commit()
            conn.close()
            flash("Employee added successfully.", "success")

        return redirect(url_for("employees"))

    return render_template("add_employee.html")


@app.route("/leave-requests")
def leave_requests():
    """Leave Requests - every request, newest first, with its current status."""
    conn = get_db_connection()
    all_requests = conn.execute(
        """
        SELECT leave_requests.id,
               employees.name AS employee_name,
               leave_requests.leave_type,
               leave_requests.from_date,
               leave_requests.to_date,
               leave_requests.reason,
               leave_requests.status
        FROM leave_requests
        JOIN employees ON employees.id = leave_requests.employee_id
        ORDER BY leave_requests.id DESC
        """
    ).fetchall()
    conn.close()
    return render_template("leave_requests.html", requests=all_requests)


@app.route("/leave-requests/apply", methods=["GET", "POST"])
def apply_leave():
    """Apply for Leave - a form that creates a new leave request (status: Pending)."""
    conn = get_db_connection()

    if request.method == "POST":
        employee_id = request.form.get("employee_id")
        leave_type = request.form.get("leave_type")
        from_date = request.form.get("from_date")
        to_date = request.form.get("to_date")
        reason = request.form.get("reason", "").strip()

        if employee_id and leave_type and from_date and to_date and reason:
            conn.execute(
                """INSERT INTO leave_requests
                   (employee_id, leave_type, from_date, to_date, reason, status)
                   VALUES (?, ?, ?, ?, ?, 'Pending')""",
                (int(employee_id), leave_type, from_date, to_date, reason),
            )
            conn.commit()
            flash("Leave request submitted.", "success")

        conn.close()
        return redirect(url_for("leave_requests"))

    all_employees = conn.execute("SELECT * FROM employees ORDER BY name").fetchall()
    conn.close()
    return render_template(
        "apply_leave.html", employees=all_employees, leave_types=LEAVE_TYPES
    )


@app.route("/leave-requests/<int:request_id>/approve", methods=["POST"])
def approve_leave(request_id):
    """Approve a pending leave request."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE leave_requests SET status = 'Approved' WHERE id = ?", (request_id,)
    )
    conn.commit()
    conn.close()
    flash("Leave request approved.", "success")
    return redirect(url_for("leave_requests"))


@app.route("/leave-requests/<int:request_id>/reject", methods=["POST"])
def reject_leave(request_id):
    """Reject a pending leave request."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE leave_requests SET status = 'Rejected' WHERE id = ?", (request_id,)
    )
    conn.commit()
    conn.close()
    flash("Leave request rejected.", "info")
    return redirect(url_for("leave_requests"))


# ---------------------------------------------------------------------------
# App entry point
# ---------------------------------------------------------------------------
# Initialized at import time so both `python app.py` and pytest (which
# imports this module) always have a ready database to work with.
init_db()

if __name__ == "__main__":
    app.run(debug=True)
