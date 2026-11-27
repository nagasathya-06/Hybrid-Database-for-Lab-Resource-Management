"""
mongo_queries.py
================
Demonstrates key MongoDB queries used by the Flask app:
  Q1 — Equipment flagged for maintenance
  Q2 — Usage logs for a specific equipment
  Q3 — Total run hours per equipment (aggregation pipeline)
  Q4 — Most active users this semester

Run: python db/mongo_queries.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db     = client[os.getenv("MONGO_DB")]

usage_col = db["usage_logs"]
maint_col = db["maintenance_logs"]


# ── Q1: Equipment flagged for maintenance ──────────────────────────────────
print("\n" + "="*55)
print("  Q1: Equipment flagged for maintenance")
print("="*55)

flagged = maint_col.find(
    {"flag_triggered": True},
    {"_id": 0, "equip_name": 1, "total_run_hours": 1,
     "threshold": 1, "hours_over_threshold": 1}
)
for doc in flagged:
    print(f"  🚨 {doc['equip_name']:<25} "
          f"{doc['total_run_hours']} hrs "
          f"(+{doc['hours_over_threshold']} over threshold)")


# ── Q2: Last 5 usage logs for Oscilloscope (equip_id=1) ───────────────────
print("\n" + "="*55)
print("  Q2: Recent usage logs — Oscilloscope")
print("="*55)

logs = usage_col.find(
    {"equip_id": 1},
    {"_id": 0, "date": 1, "start_time": 1, "end_time": 1,
     "run_hours": 1, "notes": 1}
).sort("date", -1).limit(5)

for log in logs:
    print(f"  📅 {log['date']}  {log['start_time']}–{log['end_time']}"
          f"  ({log['run_hours']}h)  — {log['notes']}")


# ── Q3: Total run hours per equipment (aggregation pipeline) ──────────────
print("\n" + "="*55)
print("  Q3: Total run hours per equipment (aggregation)")
print("="*55)

pipeline = [
    {"$group": {
        "_id":            "$equip_name",
        "total_hours":    {"$sum": "$run_hours"},
        "total_sessions": {"$count": {}}
    }},
    {"$sort": {"total_hours": -1}}
]

results = usage_col.aggregate(pipeline)
for r in results:
    print(f"  ⚙️  {r['_id']:<25} "
          f"{round(r['total_hours'],2):>8.2f} hrs  |  "
          f"{r['total_sessions']} sessions")


# ── Q4: Most active users (by number of sessions) ─────────────────────────
print("\n" + "="*55)
print("  Q4: Most active users this semester")
print("="*55)

pipeline2 = [
    {"$group": {
        "_id":     "$user_id",
        "sessions": {"$count": {}}
    }},
    {"$sort": {"sessions": -1}},
    {"$limit": 5}
]

results2 = usage_col.aggregate(pipeline2)
for r in results2:
    print(f"  👤 user_id={r['_id']}   {r['sessions']} sessions")

print("\n✅ All MongoDB queries complete.")
client.close()