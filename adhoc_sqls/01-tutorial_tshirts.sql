-- Tutorial-Teilnehmer mit T-Shirts
select user_id, last_name, first_name, max(size), sum(tutorial_tickets) as tutorial_tickets, sum(conference_tickets) as conference_tickets from (

select p.user_id, t.last_name, t.first_name, p.state, p.payment_method, ts.size,
case when tt.tutorial_ticket = true then 1 else 0 end as tutorial_tickets,
case when tt.tutorial_ticket = false then 1 else 0 end as conference_tickets
from attendees_ticket t
join attendees_purchase p on p.id = t.purchase_id
join attendees_tickettype tt on tt.id = t.ticket_type_id
left outer join attendees_tshirtsize ts on ts.id = t.shirtsize_id
) x

group by user_id, last_name, first_name
order by last_name, first_name

