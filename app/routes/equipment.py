# app/routes/equipment.py
from flask import Blueprint, render_template
from app.db.postgres import query

equipment_bp = Blueprint("equipment", __name__)

@equipment_bp.route("/")
def index():
    """Home page — list all equipment with status."""
    equipment = query("""
        SELECT e.equip_id, e.name, e.model, e.status,
               e.run_hours_total, e.maintenance_threshold_hrs,
               d.name AS department
        FROM equipment e
        JOIN departments d ON e.dept_id = d.dept_id
        ORDER BY e.name
    """)
    return render_template("index.html", equipment=equipment)