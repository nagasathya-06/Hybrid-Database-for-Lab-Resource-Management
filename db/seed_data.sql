-- ============================================================
-- Smart Equipment Booking & Maintenance System
-- seed_data.sql  --  Sample data for development & demo
-- ============================================================


-- ------------------------------------------------------------
-- Departments
-- ------------------------------------------------------------
INSERT INTO departments (name, building) VALUES
    ('Electronics & Communication',  'Block A'),
    ('Mechanical Engineering',        'Block B'),
    ('Computer Science',              'Block C'),
    ('Physics Research',              'Block D');


-- ------------------------------------------------------------
-- Users
-- ------------------------------------------------------------
INSERT INTO users (name, email, role, dept_id) VALUES
    ('Arjun Sharma',    'arjun@college.edu',    'student',    1),
    ('Priya Nair',      'priya@college.edu',    'student',    1),
    ('Dr. Mehta',       'mehta@college.edu',    'researcher', 2),
    ('Riya Patel',      'riya@college.edu',     'student',    3),
    ('Karan Singh',     'karan@college.edu',    'student',    2),
    ('Admin User',      'admin@college.edu',    'admin',      1);


-- ------------------------------------------------------------
-- Equipment
-- ------------------------------------------------------------
INSERT INTO equipment (name, model, dept_id, status, run_hours_total, maintenance_threshold_hrs) VALUES
    ('Oscilloscope',         'Tektronix TBS1052B',   1, 'available',    142.50,  150),
    ('3D Printer',           'Creality Ender 3',     2, 'available',     98.00,  200),
    ('Spectrometer',         'Ocean Optics USB2000', 4, 'available',    170.00,  150),  -- already over threshold!
    ('PCB Etching Station',  'Generic Mk-II',        1, 'available',     55.00,  150),
    ('CNC Milling Machine',  'Roland MDX-20',        2, 'maintenance',  200.00,  200),
    ('Logic Analyser',       'Saleae Logic 8',       3, 'available',     12.00,  150);


-- ------------------------------------------------------------
-- Lab Slots  (a week's worth of bookable slots)
-- ------------------------------------------------------------
INSERT INTO lab_slots (equip_id, date, start_time, end_time) VALUES
    -- Oscilloscope slots
    (1, '2026-12-01', '09:00', '11:00'),
    (1, '2026-12-01', '11:00', '13:00'),
    (1, '2026-12-02', '09:00', '11:00'),
    (1, '2026-12-02', '14:00', '16:00'),
    -- 3D Printer slots
    (2, '2026-12-01', '10:00', '13:00'),
    (2, '2026-12-02', '10:00', '13:00'),
    (2, '2026-12-03', '09:00', '12:00'),
    -- Spectrometer slots
    (3, '2026-12-01', '09:00', '10:00'),
    (3, '2026-12-01', '10:00', '11:00'),
    -- Logic Analyser slots
    (6, '2026-12-01', '09:00', '11:00'),
    (6, '2026-12-02', '11:00', '13:00');


-- ------------------------------------------------------------
-- Bookings (some slots pre-booked)
-- ------------------------------------------------------------
INSERT INTO bookings (user_id, slot_id, equip_id, status) VALUES
    (1, 1, 1, 'confirmed'),   -- Arjun booked Oscilloscope on Dec 1 09-11
    (3, 5, 2, 'confirmed'),   -- Dr. Mehta booked 3D Printer on Dec 1 10-13
    (4, 8, 3, 'confirmed');   -- Riya booked Spectrometer on Dec 1 09-10

-- Mark those slots as booked
UPDATE lab_slots SET is_booked = TRUE WHERE (slot_id, equip_id) IN ((1,1),(5,2),(8,3));


-- ------------------------------------------------------------
-- Maintenance Flags
-- ------------------------------------------------------------
-- Spectrometer is already over its threshold (170 hrs > 150 threshold)
INSERT INTO maintenance_flags (equip_id, reason, resolved) VALUES
    (3, 'Run hours exceeded threshold (170 / 150 hrs). Calibration required.', FALSE),
    (5, 'Scheduled quarterly maintenance.', TRUE);
