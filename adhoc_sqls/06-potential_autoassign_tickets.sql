DROP VIEW
	potential_autoassign_tickets
CASCADE;

CREATE VIEW
	potential_autoassign_tickets
AS
SELECT
	*
FROM
	invoice_or_paid_tickets
WHERE
	t_uid IS NULL
	AND (p_full_name = t_first_last_name OR p_display_name = t_first_last_name)
ORDER BY
	p_uid;