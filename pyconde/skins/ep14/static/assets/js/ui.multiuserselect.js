(function($) {
    $.curCSS = $.css;
    function createMultiuserSelectBox() {
        function createUserTrigger(data, selectBox) {
            var speakerPks = selectBox.data('speaker_pks');
            if (speakerPks[data.value]) {
                return;
            }
            var span = $('<span>');
            var remove = $('<a href="#" class="del" title="Delete"><i class="fa fa-fw fa-times"> </i></a>');
            var opt = data.el || $('<option>').val(data.value).text(data.label).attr('selected', 'selected').appendTo(selectBox);
            span.text(data.label);
            span.append(remove);
            speakerPks[data.value] = true;
            remove.click(function(evt) {
                evt.preventDefault();
                speakerPks[data.value] = false;
                opt.remove();
                span.remove();
            });
            return span;
        }
        if ($.ui && $.ui.autocomplete) {
            $('select.multiselect-user').each(function() {
                var $that = $(this);
                var input = $('<input />').attr('type', 'text').addClass('ui-autocomplete-input');
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
                input.autocomplete({
                        source:'/accounts/ajax/users',
                        minLength: 2
                    }).unbind('autocompleteselect').bind('autocompleteselect', function(evt, ui) {
                    evt.preventDefault();
                    $(this).val('');
                    listing.append(createUserTrigger(ui.item, $that));
                });
                $that.hide();
            });
        }
    }

    createMultiuserSelectBox();
})(jQuery);
