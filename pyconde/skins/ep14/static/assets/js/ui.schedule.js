(function($) {
    function toggleDay(event) {
        var last = $('.cmsplugin-schedule .switch.active'),
            next = $(this),
            href = next.attr('href'),
            nextEl;
        event.preventDefault();
        if (last.hasClass('active')) {
            last.removeClass('active');
            next.addClass('active');
        }
        nextEl = $(href);
        if (nextEl.hasClass('hide')) {
            nextEl.removeClass('hide');
            $(last.attr('href')).addClass('hide');
        }
        if (typeof window.history.state !== 'undefined') {
            window.history.pushState(null, document.title, href);
        }
    }

    function jumpToDayIfAppropriate() {
                var active_day = document.location.hash;
        if (active_day.match(/^#day\d+$/) !== null) {
            $('.cmsplugin-schedule .switch[href=' + active_day + ']').click();
        }
    }

    function init() {
        $('.cmsplugin-schedule .switch').on('click', toggleDay);
        jumpToDayIfAppropriate();
        window.addEventListener('popstate', jumpToDayIfAppropriate);
    }
    init();
})(jQuery);
