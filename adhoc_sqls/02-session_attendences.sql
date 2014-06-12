DROP VIEW IF EXISTS
	session_attendences
CASCADE;

CREATE VIEW
	session_attendences
AS
SELECT
	s.id sid,
	s.title,
	p.display_name,
	p.user_id uid
FROM
	schedule_session s
		INNER JOIN accounts_profile_sessions_attending sa
			ON sa.session_id = s.id
			INNER JOIN accounts_profile p
	ON p.id = sa.profile_id
ORDER BY
	sid,
	uid;