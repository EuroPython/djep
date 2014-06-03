DROP VIEW
	invoice_or_paid_tickets
CASCADE;

CREATE VIEW
	invoice_or_paid_tickets
AS
SELECT
	u.id p_uid,
	u.username p_username,
	prof.full_name p_full_name,
	prof.display_name p_display_name,
	CASE
		WHEN prof.full_name NOT IN ('', NULL) THEN prof.full_name
		ELSE prof.display_name
	END p_full_display_name,
	p.id p_id,
	p.invoice_number,
	p.state p_state,
	t.id t_id,
	t.ticket_type_id t_ticket_type_id,
	tt.name t_ticket_type,
	t.user_id t_uid,
	CASE
		WHEN tt.content_type_id = 84 THEN
			(SELECT first_name || ' ' || last_name FROM attendees_simcardticket WHERE ticket_ptr_id = t.id)
		WHEN tt.content_type_id = 85 THEN
			(SELECT first_name || ' ' || last_name FROM attendees_venueticket WHERE ticket_ptr_id = t.id)
		ELSE NULL
	END t_first_last_name
FROM
	attendees_purchase p
	INNER JOIN auth_user u
		ON p.user_id = u.id
		INNER JOIN attendees_ticket t
			ON t.purchase_id = p.id
			INNER JOIN attendees_tickettype tt
				ON tt.id = t.ticket_type_id
		INNER JOIN accounts_profile prof
			ON prof.user_id = u.id
WHERE
	p.state IN ('payment_received', 'invoice_created')
ORDER BY
	p_uid;
