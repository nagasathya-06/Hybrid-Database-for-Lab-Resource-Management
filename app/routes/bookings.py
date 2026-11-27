# app/routes/bookings.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db.postgres import query, get_connection

bookings_bp = Blueprint("bookings", __name__)

@bookings_bp.route("/book/<int:equip_id>", methods=["GET"])
def book(equip_id):
    """Show available slots for the selected equipment."""
    date = request.args.get("date")

    equipment = query(
        "SELECT * FROM equipment WHERE equip_id = %s",
        (equip_id,), fetchone=True
    )

    slots = []
    if date:
        slots = query("""
            SELECT slot_id, date, start_time, end_time
            FROM lab_slots
            WHERE equip_id = %s
              AND date = %s
              AND is_booked = FALSE
            ORDER BY start_time
        """, (equip_id, date))

    users = query("SELECT user_id, name FROM users ORDER BY name")

    return render_template("book.html",
                           equipment=equipment,
                           slots=slots,
                           users=users,
                           selected_date=date)


@bookings_bp.route("/book/<int:equip_id>/confirm", methods=["POST"])
def confirm_booking(equip_id):
    """Confirm booking using SELECT FOR UPDATE (2PL)."""
    slot_id = int(request.form["slot_id"])
    user_id = int(request.form["user_id"])

    conn = get_connection()
    conn.autocommit = False
    cur  = conn.cursor()

    try:
        # 🔒 2PL — lock the row before reading
        cur.execute("""
            SELECT is_booked FROM lab_slots
            WHERE slot_id = %s AND equip_id = %s
            FOR UPDATE
        """, (slot_id, equip_id))

        row = cur.fetchone()

        if row and not row[0]:
            cur.execute("""
                INSERT INTO bookings (user_id, slot_id, equip_id, status)
                VALUES (%s, %s, %s, 'confirmed')
            """, (user_id, slot_id, equip_id))

            cur.execute("""
                UPDATE lab_slots SET is_booked = TRUE
                WHERE slot_id = %s AND equip_id = %s
            """, (slot_id, equip_id))

            conn.commit()
            flash("✅ Booking confirmed successfully!", "success")
        else:
            conn.rollback()
            flash("❌ Sorry, that slot was just taken. Please choose another.", "danger")

    except Exception as e:
        conn.rollback()
        flash(f"❌ Error: {str(e)}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("bookings.book", equip_id=equip_id))


@bookings_bp.route("/my-bookings")
def my_bookings():
    """Show all confirmed bookings."""
    bookings = query("""
        SELECT b.booking_id, u.name AS user_name, e.name AS equipment,
               ls.date, ls.start_time, ls.end_time, b.status, b.booked_at
        FROM bookings b
        JOIN users     u  ON b.user_id  = u.user_id
        JOIN lab_slots ls ON b.slot_id  = ls.slot_id
                         AND b.equip_id = ls.equip_id
        JOIN equipment e  ON ls.equip_id = e.equip_id
        ORDER BY ls.date DESC
    """)
    return render_template("my_bookings.html", bookings=bookings)