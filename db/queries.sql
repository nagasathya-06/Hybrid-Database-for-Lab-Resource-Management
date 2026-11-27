-- Q1: Show all available (unbooked) slots for a given equipment on a given date
-- Usage: User picks equipment → app shows free slots for that day

SELECT
    ls.slot_id,
    e.name           AS equipment_name,
    ls.date,
    ls.start_time,
    ls.end_time
FROM lab_slots ls
JOIN equipment e ON ls.equip_id = e.equip_id
WHERE ls.equip_id = 1              -- replace 1 with the equipment you want
  AND ls.date    = '2026-12-01'    -- replace with selected date
  AND ls.is_booked = FALSE
  AND e.status   = 'available'     -- don't show slots for machines under maintenance
ORDER BY ls.start_time;