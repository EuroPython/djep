DROP VIEW
	unassigned_tickets_per_purchase_user
CASCADE;

CREATE VIEW
	unassigned_tickets_per_purchase_user
AS
SELECT
	p_uid,
	p_username,
	p_full_display_name,
	t_ticket_type_id,
	count(p_uid) cnt
FROM
	invoice_or_paid_tickets
WHERE
	t_uid IS NULL
GROUP BY
	p_uid,
	p_username,
	t_ticket_type_id,
	p_full_display_name
ORDER BY
	p_uid;
