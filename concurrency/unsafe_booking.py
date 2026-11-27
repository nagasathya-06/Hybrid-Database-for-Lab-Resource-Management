"""
unsafe_booking.py
=================
Demonstrates the DOUBLE BOOKING problem.

Two threads simulate two users booking the SAME slot at the SAME time.
There is NO transaction protection here — just a plain check-then-insert.

Expected result: BOTH bookings succeed → double booking occurs 💥
"""


import threading
import time
import psycopg2
from dotenv import load_dotenv
import os
from pathlib import Path

# Explicitly locate .env in the project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


DB_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "port":     os.getenv("DB_PORT"),
    "dbname":   os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# We'll try to double-book slot_id=2, equip_id=1
# (Oscilloscope, Dec 1, 11:00–13:00 — currently free)
TARGET_SLOT_ID  = 2
TARGET_EQUIP_ID = 1


def unsafe_book(user_id, user_name):
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True          # no transaction wrapping
    cur = conn.cursor()

    print(f"[{user_name}] Checking if slot {TARGET_SLOT_ID} is available...")
    cur.execute(
        "SELECT is_booked FROM lab_slots WHERE slot_id = %s AND equip_id = %s",
        (TARGET_SLOT_ID, TARGET_EQUIP_ID)
    )
    row = cur.fetchone()

    if row and not row[0]:
        # Simulate a tiny delay between check and insert
        # (This is where the race condition happens in real life)
        time.sleep(0.1)

        print(f"[{user_name}] Slot is free! Booking now...")
        cur.execute(
            """
            INSERT INTO bookings (user_id, slot_id, equip_id, status)
            VALUES (%s, %s, %s, 'confirmed')
            """,
            (user_id, TARGET_SLOT_ID, TARGET_EQUIP_ID)
        )
        cur.execute(
            "UPDATE lab_slots SET is_booked = TRUE WHERE slot_id = %s AND equip_id = %s",
            (TARGET_SLOT_ID, TARGET_EQUIP_ID)
        )
        print(f"[{user_name}] ✅ Booking INSERTED (user_id={user_id})")
    else:
        print(f"[{user_name}] ❌ Slot already taken.")

    cur.close()
    conn.close()


def reset_slot():
    """Reset the slot to unbooked state before each demo run."""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DELETE FROM bookings WHERE slot_id = %s AND equip_id = %s",
                (TARGET_SLOT_ID, TARGET_EQUIP_ID))
    cur.execute("UPDATE lab_slots SET is_booked = FALSE WHERE slot_id = %s AND equip_id = %s",
                (TARGET_SLOT_ID, TARGET_EQUIP_ID))
    cur.close()
    conn.close()
    print("🔄 Slot reset to unbooked.\n")


if __name__ == "__main__":
    reset_slot()

    print("=" * 55)
    print("  UNSAFE BOOKING DEMO — No transaction protection")
    print("  Two users booking the SAME slot simultaneously")
    print("=" * 55 + "\n")

    # Two threads = two users hitting Book at the same moment
    t1 = threading.Thread(target=unsafe_book, args=(2, "User-Priya"))
    t2 = threading.Thread(target=unsafe_book, args=(4, "User-Riya"))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Show the damage
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        "SELECT booking_id, user_id, slot_id FROM bookings WHERE slot_id = %s AND equip_id = %s",
        (TARGET_SLOT_ID, TARGET_EQUIP_ID)
    )
    rows = cur.fetchall()
    print(f"\n📋 Bookings in DB for slot {TARGET_SLOT_ID}: {len(rows)} found")
    for r in rows:
        print(f"   booking_id={r[0]}, user_id={r[1]}, slot_id={r[2]}")
    if len(rows) > 1:
        print("\n💥 DOUBLE BOOKING OCCURRED — This is the problem we need to fix!\n")
    cur.close()
    conn.close()