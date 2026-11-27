"""
seed_mongo.py
=============
Generates a semester's worth of equipment usage logs in MongoDB.
Also builds and updates the maintenance_logs collection,
triggering a flag when run_hours cross the threshold.

Run once to populate: python db/seed_mongo.py
"""

import os
import random
from datetime import datetime, timedelta, date
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db     = client[os.getenv("MONGO_DB")]

# Collections
usage_col = db["usage_logs"]
maint_col = db["maintenance_logs"]

# Clear old data for clean re-runs
usage_col.drop()
maint_col.drop()
print("🧹 Cleared old collections.")

# Equipment list — mirrors our PostgreSQL equipment table
EQUIPMENT = [
    {"equip_id": 1, "name": "Oscilloscope",         "threshold": 150},
    {"equip_id": 2, "name": "3D Printer",            "threshold": 200},
    {"equip_id": 3, "name": "Spectrometer",          "threshold": 150},
    {"equip_id": 4, "name": "PCB Etching Station",   "threshold": 150},
    {"equip_id": 6, "name": "Logic Analyser",        "threshold": 150},
]

USERS = [1, 2, 3, 4, 5]   # mirrors our PostgreSQL users

NOTES_POOL = [
    "Routine lab session",
    "Final year project work",
    "Research experiment — batch 3",
    "Calibration test run",
    "Student practicum session",
    "Faculty-supervised experiment",
    "Signal analysis for mini project",
    "PCB prototype testing",
]

# Simulate a full semester: Aug 1 to Nov 30
SEMESTER_START = date(2026, 8, 1)
SEMESTER_END   = date(2026, 11, 30)

# Track cumulative run hours per equipment (starting from seed_data values)
run_hours_tracker = {
    1: 142.5,   # Oscilloscope — already seeded in PostgreSQL
    2: 98.0,    # 3D Printer
    3: 170.0,   # Spectrometer — already over threshold
    4: 55.0,    # PCB Etching
    6: 12.0,    # Logic Analyser
}

usage_docs = []

print("⚙️  Generating usage logs...")

current_date = SEMESTER_START
while current_date <= SEMESTER_END:
    # Skip Sundays
    if current_date.weekday() != 6:
        for equip in EQUIPMENT:
            # ~60% chance a machine is used on any given day
            if random.random() < 0.6:
                # Random session: 1–4 hours
                session_hours = round(random.uniform(1.0, 4.0), 2)
                start_hour    = random.randint(8, 16)
                start_time    = f"{start_hour:02d}:00"
                end_hour      = start_hour + int(session_hours)
                end_time      = f"{min(end_hour, 20):02d}:00"

                run_hours_tracker[equip["equip_id"]] += session_hours

                doc = {
                    "equip_id":   equip["equip_id"],
                    "equip_name": equip["name"],
                    "user_id":    random.choice(USERS),
                    "date":       current_date.strftime("%Y-%m-%d"),
                    "start_time": start_time,
                    "end_time":   end_time,
                    "run_hours":  session_hours,
                    "notes":      random.choice(NOTES_POOL),
                    "logged_at":  datetime.now(),
                }
                usage_docs.append(doc)

    current_date += timedelta(days=1)

usage_col.insert_many(usage_docs)
print(f"✅ Inserted {len(usage_docs)} usage log documents.\n")

# Build maintenance_logs — one document per equipment
print("🔧 Building maintenance logs...")
maint_docs = []

for equip in EQUIPMENT:
    total_hrs    = round(run_hours_tracker[equip["equip_id"]], 2)
    flag         = total_hrs >= equip["threshold"]
    hours_over   = round(total_hrs - equip["threshold"], 2) if flag else 0

    doc = {
        "equip_id":        equip["equip_id"],
        "equip_name":      equip["name"],
        "total_run_hours": total_hrs,
        "threshold":       equip["threshold"],
        "flag_triggered":  flag,
        "hours_over_threshold": hours_over,
        "last_updated":    datetime.now(),
    }
    maint_docs.append(doc)

    status = "🚨 FLAGGED" if flag else "✅ OK"
    print(f"  {equip['name']:<25} {total_hrs:>8.2f} hrs / {equip['threshold']} threshold  {status}")

maint_col.insert_many(maint_docs)
print(f"\n✅ Inserted {len(maint_docs)} maintenance log documents.")
print("\n🍃 MongoDB seeding complete!")
client.close()