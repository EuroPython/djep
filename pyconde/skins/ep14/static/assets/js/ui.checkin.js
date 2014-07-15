(function($) {
    function addTicket(event) {
        var extra_ticket_holder = $('#extra-ticket');
        var extra_ticket_form = extra_ticket_holder.children();
        var total = parseInt($('#id_form-TOTAL_FORMS').val())
        var next = total;  // no +1 since 0-indexed
        var new_form = extra_ticket_form.clone();
        $('[name*=-__prefix__-], [id*=-__prefix__-], [for*=-__prefix__-]', new_form).each(function() {
            var repl = '-' + next + '-';
            var val = $(this).attr('name');
            if (val !== undefined) {
                $(this).attr('name', val.replace('-__prefix__-', repl));
            }
            val = $(this).attr('id');
            if (val !== undefined) {
                $(this).attr('id', val.replace('-__prefix__-', repl));
            }
            val = $(this).attr('for');
            if (val !== undefined) {
                $(this).attr('for', val.replace('-__prefix__-', repl));
            }
        });
        new_form.insertBefore(extra_ticket_holder);
        $('#id_form-TOTAL_FORMS').val(total + 1);
    }

    function init() {
        $('#add-ticket').on('click', addTicket);
    }
    init();
})(jQuery);
