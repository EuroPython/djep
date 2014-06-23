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
	AND (LOWER(p_full_name) = LOWER(t_first_last_name) OR LOWER(p_display_name) = LOWER(t_first_last_name))
	AND p_state = 'payment_received'
ORDER BY
	p_uid;