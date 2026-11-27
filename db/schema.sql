-- ============================================================
-- Smart Equipment Booking & Maintenance System
-- schema.sql  --  DDL (Data Definition Language)
-- Run this file in psql to create the full database schema.
-- ============================================================

-- Drop tables in reverse dependency order (safe re-run)
DROP TABLE IF EXISTS maintenance_flags CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS lab_slots CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS departments CASCADE;


-- ------------------------------------------------------------
-- 1. DEPARTMENT
--    One department owns many equipment items and has many users.
-- ------------------------------------------------------------
CREATE TABLE departments (
    dept_id     SERIAL          PRIMARY KEY,
    name        VARCHAR(100)    NOT NULL UNIQUE,
    building    VARCHAR(100)    NOT NULL
);


-- ------------------------------------------------------------
-- 2. USER
--    A user belongs to exactly one department.
--    role: 'student' | 'researcher' | 'admin'
-- ------------------------------------------------------------
CREATE TABLE users (
    user_id     SERIAL          PRIMARY KEY,
    name        VARCHAR(100)    NOT NULL,
    email       VARCHAR(150)    NOT NULL UNIQUE,
    role        VARCHAR(20)     NOT NULL DEFAULT 'student'
                                CHECK (role IN ('student', 'researcher', 'admin')),
    dept_id     INT             NOT NULL,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
);


-- ------------------------------------------------------------
-- 3. EQUIPMENT
--    Owned by one department. Tracks cumulative run hours
--    for maintenance threshold triggering.
--    status: 'available' | 'booked' | 'maintenance'
-- ------------------------------------------------------------
CREATE TABLE equipment (
    equip_id            SERIAL          PRIMARY KEY,
    name                VARCHAR(150)    NOT NULL,
    model               VARCHAR(100),
    dept_id             INT             NOT NULL,
    status              VARCHAR(20)     NOT NULL DEFAULT 'available'
                                        CHECK (status IN ('available', 'booked', 'maintenance')),
    run_hours_total     NUMERIC(8,2)    NOT NULL DEFAULT 0.00,
    maintenance_threshold_hrs  INT      NOT NULL DEFAULT 150,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
);


-- ------------------------------------------------------------
-- 4. LAB SLOT  (WEAK ENTITY)
--    A time slot that only exists for a specific equipment item.
--    Composite PK: (slot_id, equip_id) — slot_id alone is not enough.
--    UNIQUE constraint on (equip_id, date, start_time) prevents
--    the same machine being double-listed for the same window.
-- ------------------------------------------------------------
CREATE TABLE lab_slots (
    slot_id     SERIAL          NOT NULL,
    equip_id    INT             NOT NULL,
    date        DATE            NOT NULL,
    start_time  TIME            NOT NULL,
    end_time    TIME            NOT NULL,
    is_booked   BOOLEAN         NOT NULL DEFAULT FALSE,

    PRIMARY KEY (slot_id, equip_id),                            -- composite PK (weak entity)
    FOREIGN KEY (equip_id) REFERENCES equipment(equip_id) ON DELETE CASCADE,
    CONSTRAINT no_overlap UNIQUE (equip_id, date, start_time),  -- no duplicate slots
    CONSTRAINT valid_times CHECK (end_time > start_time)
);


-- ------------------------------------------------------------
-- 5. BOOKING
--    Links a user to a lab slot. The 1:1 between booking and
--    slot is enforced by the UNIQUE constraint on slot_id+equip_id.
--    status: 'confirmed' | 'cancelled' | 'completed'
-- ------------------------------------------------------------
CREATE TABLE bookings (
    booking_id  SERIAL          PRIMARY KEY,
    user_id     INT             NOT NULL,
    slot_id     INT             NOT NULL,
    equip_id    INT             NOT NULL,    -- needed to reference composite FK
    booked_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    status      VARCHAR(20)     NOT NULL DEFAULT 'confirmed'
                                CHECK (status IN ('confirmed', 'cancelled', 'completed')),

    FOREIGN KEY (user_id)               REFERENCES users(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (slot_id, equip_id)     REFERENCES lab_slots(slot_id, equip_id),
    UNIQUE (slot_id, equip_id)          -- enforces 1:1 — one booking per slot
);


-- ------------------------------------------------------------
-- 6. MAINTENANCE FLAG
--    Auto-raised when run_hours_total crosses the threshold.
--    Can also be raised manually by admin.
-- ------------------------------------------------------------
CREATE TABLE maintenance_flags (
    flag_id     SERIAL          PRIMARY KEY,
    equip_id    INT             NOT NULL,
    flagged_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    reason      TEXT,
    resolved    BOOLEAN         NOT NULL DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,

    FOREIGN KEY (equip_id) REFERENCES equipment(equip_id) ON DELETE CASCADE
);


-- ============================================================
-- INDEXES — speed up the most common queries
-- ============================================================
CREATE INDEX idx_lab_slots_equip_date  ON lab_slots (equip_id, date);
CREATE INDEX idx_bookings_user         ON bookings (user_id);
CREATE INDEX idx_bookings_slot         ON bookings (slot_id, equip_id);
CREATE INDEX idx_maint_equip           ON maintenance_flags (equip_id);
