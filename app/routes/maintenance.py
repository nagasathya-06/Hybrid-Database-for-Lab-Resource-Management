# app/routes/maintenance.py
from flask import Blueprint, render_template
from app.db.mongo import get_mongo_db

maintenance_bp = Blueprint("maintenance", __name__)

@maintenance_bp.route("/dashboard")
def dashboard():
    """Maintenance dashboard — data from MongoDB."""
    db    = get_mongo_db()
    logs  = list(db["maintenance_logs"].find(
        {}, {"_id": 0}
    ).sort("total_run_hours", -1))

    # Recent usage logs (last 10)
    recent = list(db["usage_logs"].find(
        {}, {"_id": 0, "equip_name": 1, "date": 1,
             "start_time": 1, "end_time": 1, "run_hours": 1, "notes": 1}
    ).sort("date", -1).limit(10))

    return render_template("dashboard.html", logs=logs, recent=recent)