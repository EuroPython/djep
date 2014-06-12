DROP VIEW
	schedule_active_speakers
CASCADE;

CREATE VIEW
	schedule_active_speakers
AS
SELECT DISTINCT
	u.id uid,
	u.username,
	p.full_name,
	p.display_name
FROM
	auth_user u
	INNER JOIN accounts_profile p
		ON u.id = p.user_id
		INNER JOIN (
			SELECT
				s.user_id
			FROM
				schedule_session ss
				INNER JOIN speakers_speaker s
					ON ss.speaker_id = s.id AND ss.released = True
			UNION ALL
			SELECT
				s.user_id
			FROM
				schedule_session ss
				INNER JOIN schedule_session_additional_speakers ssas
					ON ss.id = ssas.session_id AND ss.released = True
						INNER JOIN speakers_speaker s
							ON ssas.speaker_id = s.id
		) s
			ON u.id = s.user_id
ORDER BY
	u.id;
