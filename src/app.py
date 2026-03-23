"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

try:
    from .database import (
        activity_exists,
        init_db,
        list_activities,
        registration_exists,
        signup_for_activity as create_registration,
        unregister_from_activity as delete_registration,
    )
except ImportError:
    from database import (
        activity_exists,
        init_db,
        list_activities,
        registration_exists,
        signup_for_activity as create_registration,
        unregister_from_activity as delete_registration,
    )

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

init_db()

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return list_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if not activity_exists(activity_name):
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if registration_exists(activity_name, email):
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    create_registration(activity_name, email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if not activity_exists(activity_name):
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is signed up
    if not registration_exists(activity_name, email):
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    delete_registration(activity_name, email)
    return {"message": f"Unregistered {email} from {activity_name}"}

