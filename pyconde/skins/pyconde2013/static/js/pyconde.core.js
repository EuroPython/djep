/*global jQuery */
var pyconde = (function($) {
    function createMultiuserSelectBox() {
        function createUserTrigger(data, selectBox) {
            var speakerPks = selectBox.data('speaker_pks');
            if (speakerPks[data.value]) {
                return;
            }
            var span = $('<span>');
            var remove = $('<a href="#" class="del">x</a>');
            var opt = data.el || $('<option>').val(data.value).text(data.label).attr('selected', 'selected').appendTo(selectBox);
            span.text(data.label);
            span.append(remove);
            speakerPks[data.value] = true;
            remove.click(function(evt) {
                evt.preventDefault();
                opt.remove();
                span.remove();
            });
            return span;
        }
        if ($.ui && $.ui.autocomplete) {
            $('select.multiselect-user').each(function() {
                var $that = $(this);
                var input = $('<input />').attr('type', 'text');
                var listing = $('<div>').addClass('ui-autocomplete-result');
                $that.data('speaker_pks', {});
                input.insertAfter($that);
                listing.insertAfter(input);
                $('option', $that).each(function() {
                    var $opt = $(this);
                    var value = $opt.val();
                    if (value === '') {
                        return;
                    }
                    listing.append(createUserTrigger({'label': $opt.text(), 'value': value, 'el': $opt}, $that));
                });
                input.autocomplete({source:'/accounts/ajax/users'}).unbind('autocompleteselect').bind('autocompleteselect', function(evt, ui) {
                    evt.preventDefault();
                    $(this).val('');
                    listing.append(createUserTrigger(ui.item, $that));
                });
                $that.hide();
            });
        }
    }
    function createSponsorSlides() {
        $('.cmsplugin-sponsorlist.split').each(function() {
            var container = $(this), height;
            var slideContainer = $(this).find('> div');
            var numSlides = slideContainer.find('ul').length;
            if (container.hasClass('slides-2rows')) {
                height = 150;
            } else if (container.hasClass('slides-3rows')){
                height = 225;
            } else {
                height = 75;
            }
            if (numSlides < 2) {
                return;
            }
            slideContainer.slidesjs({
                width: container.width(),
                height: 150,
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
                        container.find('.slidesjs-pagination-item a').removeClass('active');
                        container.find('a[data-slidesjs-item=' + (num % numSlides) + ']').addClass('active');
                    },
                    loaded: function(num) {
                        container.find('a[data-slidesjs-item=' + (num-1) + ']').addClass('active');
                    }
                }
            });
        });
    }

    function init() {
        createSponsorSlides();
        $(createMultiuserSelectBox);
        $('div.navbar').mouseenter(function() {
            var $that = $(this);
            window.setTimeout(function() {
                if ($that.is(':hover')) {
                    $('#dropout-menu').slideDown();
                }
            }, 300);
        }).mouseleave(function() {
            $('#dropout-menu').slideUp();
        });
    }

    init();
})(jQuery);