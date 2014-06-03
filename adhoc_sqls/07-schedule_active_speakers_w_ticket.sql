DROP VIEW
	schedule_active_speakers_w_ticket
CASCADE;

CREATE VIEW
	schedule_active_speakers_w_ticket
AS
SELECT DISTINCT
	s.*
FROM
	schedule_active_speakers s
		INNER JOIN invoice_or_paid_tickets t
			ON s.uid IN (t.p_uid, t.t_uid)
ORDER BY
	s.uid;