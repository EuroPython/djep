var ep = ep || {};

/**
 * This module provides the integration code for the used form-validation
 * library.
 */
ep.validation = (function($) {
    /**
     * Here is the actual validation confirmation stored that should be used on
     * a page with the give class.
     */
    var PAGE_CONFIGS = {
        'registration': function() {
            var form = $('#content > form');
            form.find('*[name=accept_privacy_policy]').attr('required', 'required');
            form.find('*[name=email]').attr('data-parsley-type', 'email');
            form.find('*[name=twitter]').attr('data-parsley-twittername', '');
            initForm(form);
        }
    };

    /**
     * Initializes the given form for use with Parsley and already marks
     * all fields as mandatory that have a label ending with an asterisk.
     *
     * @param form jQuery form object
     */
    function initForm(form) {
        // Mark all fields as required that feature a label with an asterisk
        form.find('.form-group').each(function() {
            var group = $(this);
            if (group.find('span.asteriskField').length) {
                var input = group.find('input');
                if (input.length) {
                    input.attr('required', 'required');
                }
            }
        });

        form.parsley({
            trigger: 'blur',
            successClass: 'ok',
            errorClass: 'error',
            errorsWrapper: '<span class="help-block error"><strong><i class="fa fa-fw fa-times"></i></strong></span>',
            errorTemplate: '<span></span>'
        });
        form.find('.help-block.error').hide();
    }

    function registerGlobalListeners() {
        $.listen('parsley:field:validate', function(field) {
            field.$element.parents('.form-group').removeClass('has-error').find('.help-block.error').hide();
        });

        $.listen('parsley:field:error', function(field) {
            field.$element.parents('.form-group').addClass('has-error').find('.help-block.error').show();
        });
    }

    /**
     * Initializes the validation logic for the first class for which a
     * configuration can be found in the PAGE_CONFIGS object.
     */
    function initValidationForPage() {
        var classes = ($('body').attr('class') || "").split(" ");
        for (var i = 0, len = classes.length; i < len; i++) {
            var cls = classes[i];
            if (typeof PAGE_CONFIGS[cls] !== 'undefined') {
                PAGE_CONFIGS[cls]();
                break;
            }
        }
    }

    var $V = ParsleyValidator;
    $V.setLocale(document.documentElement.lang);

    $V.addValidator('twittername', function(value, requirement) {
        if (value && value.indexOf('@') === 0) {
            return false;
        }
        return true;
    }, 10);
    $V.addMessage('en', 'twittername', 'Please omit the @ at the start of the twitter username');
    $V.addMessage('de', 'twittername', 'Bitte schreiben Sie Ihren Twitter-Namen ohne @ am Anfang');

    registerGlobalListeners();
    initValidationForPage();

    return {};
}(jQuery));
