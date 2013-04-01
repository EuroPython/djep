var pyconde = (function($) {
    function createSponsorSlides() {
        $('.cmsplugin-sponsorlist.split').each(function() {
            var container = $(this), height;
            var slideContainer = $(this).find('> div');
            var numSlides = slideContainer.find('ul').length;
            if (container.hasClass('slides-2rows')) {
                height = 150;
            } else {
                height = 75;
            }
            if (numSlides < 2) return;
            slideContainer.slidesjs({
                width: container.width(), height: 150,
                navigation: {active: false},
                effect: {fade: {speed: 1000}},
                pagination: {effect: 'fade'},
                play: {
                    effect: "fade",
                    auto: true,
                    interval: 5000,
                    pauseOnHover: true
                },
                callback: {
                    start: function(num) {
                        console.log("Start: ", num);
                        container.find('.slidesjs-pagination-item a').removeClass('active');
                        container.find('a[data-slidesjs-item=' + (num % numSlides) + ']').addClass('active');
                    },
                    loaded: function(num) {
                        console.log("Loaded: ", num);
                        container.find('a[data-slidesjs-item=' + (num-1) + ']').addClass('active');
                    }
                }
            });
        });
    }

    function init() {
        createSponsorSlides();
    }

    init();
})(jQuery);