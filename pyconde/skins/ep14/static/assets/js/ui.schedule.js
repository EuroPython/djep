(function($) {
    function toggleDay(event) {
        var last = $('.cmsplugin-schedule .switch.active'),
            next = $(this);
        if (last.hasClass('active')) {
            last.removeClass('active');
            next.addClass('active');
        }
        if ($(next.attr('href')).hasClass('hide')) {
            $(next.attr('href')).removeClass('hide');
            $(last.attr('href')).addClass('hide');
        }
        event.preventDefault();
    }

    function init() {
        $('.cmsplugin-schedule .switch').on('click', toggleDay);
        active_day = document.location.hash
        if (active_day.match(/^#day\d+$/) !== null) {
            $('.cmsplugin-schedule .switch[href=' + active_day + ']').click();
        }
    }
    init();
})(jQuery);
