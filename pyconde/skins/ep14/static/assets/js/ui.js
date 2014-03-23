/*global gettext, $*/
var ep = ep || {};
ep.ui = (function($) {
    function wrapFileUploads() {
        $('input[type=file]').each(function() {
            var statusLine = $('<span>').addClass('status');
            var wrapper = $('<span>').addClass('input-wrapper').addClass('btn-primary').text(gettext('Choose a file'));
            var outerWrapper = $('<span>').addClass('file-outer-wrapper');
            $(this).wrap(wrapper);
            $(this).parent('span').wrap(outerWrapper);
            $(this).parents('.file-outer-wrapper').append(statusLine);
        });

        $('body').on('change', 'input[type=file]', function(evt) {
            var filename = "";
            if ($(this)[0].files) {
                filename = $(this)[0].files[0].name;
            }
            $(this).parents('.file-outer-wrapper').find('.status').text(filename);
        });
    }

    function overrideOrbitUi() {
        $('.orbit-list').each(function(idx, container) {
            $(container).on('ready.fndtn.orbit', function(evt) {
                // Now we replace the previous and next buttons with custom
                // icons.
                var container = $(this).parent(),
                    next = container.find('.orbit-next > span'),
                    prev = container.find('.orbit-prev > span');
                prev.append('<i class="fa fa-fw fa-angle-left">');
                next.append('<i class="fa fa-fw fa-angle-right">');
            });
        });
    }

    function toggleMenuIcons(holder) {
        $(holder).hover(function() {
            $(this).find('> a > i')
                .removeClass('fa-angle-left')
                .addClass('fa-angle-down');
        }, function() {
            $(this).find('> a > i')
                .removeClass('fa-angle-down')
                .addClass('fa-angle-left');
        });
    }

    function handleAccountMenuOnTouch(holder) {
        // We only need this on touch devices
        if (!$('html').hasClass('touch')) {
            return;
        }
        $(holder + ' > a').on('click', function(evt) {
            if ($(window).width() < 889) {
                evt.preventDefault();
                var icon = $(this).find('> i');
                if (icon.hasClass('fa-angle-down')) {
                    icon.removeClass('fa-angle-down')
                        .addClass('fa-angle-left');
                } else {
                    icon.removeClass('fa-angle-left')
                        .addClass('fa-angle-down');
                }
                $(holder + ' > ul').toggle();
                return;
            }
        });
    }

    function init() {
        wrapFileUploads();
        overrideOrbitUi();
        toggleMenuIcons('#sponsorshipbox');
        handleAccountMenuOnTouch('#sponsorshipbox');
        toggleMenuIcons('#reviewbox');
        handleAccountMenuOnTouch('#reviewbox');
        toggleMenuIcons('#accountbox');
        handleAccountMenuOnTouch('#accountbox');
    }

    init();
    return {};
}(jQuery));
