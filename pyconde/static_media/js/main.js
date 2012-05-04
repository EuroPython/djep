var pyconde = (function() {
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

    function hideField(field) {
        var val = field.val();
        var selectbox = $('select', field);
        var required = !!($('.requiredField', field).length);
        if (selectbox.length && required && !val) {
            selectbox.val($('option[value!=""]', field).val());
        }
        field.data('oldValue', val);
        field.fadeOut();
    }

    function restoreField(field) {
        field.val(field.data('oldValue'));
        field.fadeIn();
    }

    function handleKindChange($that) {
        if ($(':selected', $that).text() === 'Tutorial') {
            hideField($('#div_id_track'));
            hideField($('#div_id_duration'));
        } else {
            restoreField($('#div_id_track'));
            restoreField($('#div_id_duration'));
        }
    }

    function init() {
        var body = $('body');
        $('.help-block.extended').each(function() {
            var trigger = $('> .trigger', this);
            trigger.prepend('<i class="icon-question-sign"></i>&nbsp;');
            var body = $('> .body', this);
            body.hide();
            trigger.bind('click', function() {
                body.slideToggle();
            });
        });
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
                    if (value === '') return;
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
        if (body.hasClass('proposal-form')) {
            handleKindChange($('select#id_kind').bind('change', function(evt) {
                handleKindChange($(this));
            }));
        }
    }

    return {
        init: init
    };
}());