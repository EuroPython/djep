DROP VIEW IF EXISTS
	income
CASCADE;

CREATE VIEW
	income
AS
SELECT
	t.p_state state,
	tt.name,
	count(tt.id),
	sum(tt.fee)
FROM
	invoice_or_paid_tickets t
	INNER JOIN attendees_tickettype tt
		ON t.t_ticket_type_id = tt.id
GROUP BY
	p_state,
	tt.product_number,
	tt.name
ORDER BY
	t.p_state,
	tt.product_number
;
