DROP VIEW IF EXISTS
	schedule_active_speakers_wo_ticket
CASCADE;

CREATE VIEW
	schedule_active_speakers_wo_ticket
AS
SELECT DISTINCT
	s.*
FROM
	schedule_active_speakers s
WHERE
	s.uid NOT IN (
		SELECT
			uid
		FROM
			schedule_active_speakers_w_ticket
	)
ORDER BY
	s.uid;