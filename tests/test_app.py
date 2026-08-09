"""
Basic pytest test cases for the Employee Leave Management Portal.

These are intentionally simple so a Jenkins "Test" stage can run them
(`pytest`) with no extra setup, and so a broken change fails the pipeline
before it ever reaches deploy.
"""

import os
import sys

# Make the project root importable when pytest is run from the tests/ folder.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from app import app as flask_app, get_db_connection


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client


def test_application_loads(client):
    """The application's home route should respond successfully."""
    response = client.get("/")
    assert response.status_code == 200


def test_dashboard_loads(client):
    """Dashboard should load and show its stat labels."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Total Employees" in response.data
    assert b"Pending Requests" in response.data
    assert b"Approved Requests" in response.data


def test_employee_can_be_added(client):
    """Submitting the Add Employee form should create a new employee."""
    response = client.post(
        "/employees/add",
        data={
            "name": "Test Employee",
            "department": "Quality Assurance",
            "email": "test.employee@company.com",
            "leave_balance": "20",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Test Employee" in response.data


def test_leave_request_can_be_created(client):
    """Submitting the Apply for Leave form should create a new leave request."""
    response = client.post(
        "/leave-requests/apply",
        data={
            "employee_id": "1",
            "leave_type": "Casual Leave",
            "from_date": "2026-09-01",
            "to_date": "2026-09-02",
            "reason": "Automated test leave request",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Automated test leave request" in response.data


def test_leave_request_can_be_approved(client):
    """A pending leave request should be approvable and its status should update."""
    client.post(
        "/leave-requests/apply",
        data={
            "employee_id": "2",
            "leave_type": "Sick Leave",
            "from_date": "2026-09-05",
            "to_date": "2026-09-06",
            "reason": "Approval workflow test",
        },
        follow_redirects=True,
    )

    conn = get_db_connection()
    new_request = conn.execute(
        "SELECT id, status FROM leave_requests WHERE reason = ?",
        ("Approval workflow test",),
    ).fetchone()
    conn.close()

    assert new_request is not None
    assert new_request["status"] == "Approved"

    response = client.post(
        f"/leave-requests/{new_request['id']}/approve", follow_redirects=True
    )
    assert response.status_code == 200

    conn = get_db_connection()
    updated_request = conn.execute(
        "SELECT status FROM leave_requests WHERE id = ?", (new_request["id"],)
    ).fetchone()
    conn.close()

    assert updated_request["status"] == "Approved"
