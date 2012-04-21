var pyconde = (function() {
    function init() {
        $('.help-block.extended').each(function() {
            var trigger = $('> .trigger', this);
            trigger.prepend('<i class="icon-question-sign"></i>&nbsp;');
            var body = $('> .body', this);
            body.hide();
            trigger.bind('click', function() {
                body.slideToggle();
            });
        });
    }

    return {
        init: init
    };
})();