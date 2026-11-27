"""
safe_booking.py
===============
Demonstrates the FIX using Two-Phase Locking (2PL).

SELECT ... FOR UPDATE locks the row the moment we read it.
No other transaction can read OR write that row until we COMMIT.

Expected result: One user books successfully, the other is REJECTED ✅
"""

import threading
import time
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "port":     os.getenv("DB_PORT"),
    "dbname":   os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

TARGET_SLOT_ID  = 2
TARGET_EQUIP_ID = 1


def safe_book(user_id, user_name):
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False         # manual transaction control
    cur = conn.cursor()

    try:
        print(f"[{user_name}] BEGIN transaction")

        # 🔒 SELECT FOR UPDATE — acquires a row-level lock immediately
        # Any other transaction trying to SELECT FOR UPDATE the same row WAITS here
        cur.execute(
            """
            SELECT is_booked FROM lab_slots
            WHERE slot_id = %s AND equip_id = %s
            FOR UPDATE
            """,
            (TARGET_SLOT_ID, TARGET_EQUIP_ID)
        )
        row = cur.fetchone()

        print(f"[{user_name}] Lock acquired — checking availability...")
        time.sleep(0.1)             # simulate processing time

        if row and not row[0]:
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
            conn.commit()           # 🔓 lock released here
            print(f"[{user_name}] ✅ Booking CONFIRMED and committed. Lock released.")
        else:
            conn.rollback()
            print(f"[{user_name}] ❌ Slot already taken. Transaction rolled back.")

    except Exception as e:
        conn.rollback()
        print(f"[{user_name}] ❌ Error: {e}. Rolled back.")
    finally:
        cur.close()
        conn.close()


def reset_slot():
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
    print("  SAFE BOOKING DEMO — Two-Phase Locking (2PL)")
    print("  Two users booking the SAME slot simultaneously")
    print("=" * 55 + "\n")

    t1 = threading.Thread(target=safe_book, args=(2, "User-Priya"))
    t2 = threading.Thread(target=safe_book, args=(4, "User-Riya"))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Show the result
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
    if len(rows) == 1:
        print("\n✅ EXACTLY ONE BOOKING — 2PL worked correctly!\n")
    cur.close()
    conn.close()