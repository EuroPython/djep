(function($) {
    var currentSelection = [],
        allowedNames = [],
        lang = "en",
        form,
        field,
        ticketType,
        container;

    function getSpecifiedFieldNames(str) {
        return str.split(/\s*,\s*/);
    }

    function writeBack (evt) {
        // First remove all fields from the selection that
        // are not available for the current ticketType
        currentSelection = currentSelection.filter(function(elem) {
            for (var i = 0, len = allowedNames.length; i < len; i++) {
                if (allowedNames[i].name === elem) {
                    return true;
                }
            }
            return false;
        });
        field.val(currentSelection.join(","));
        container.find('> div').remove();
        field.show();
    }
    function getPossibleFieldNames(ticketType, cb) {
        return $.ajax({
            url: '/' + lang + '/tickets/admin/ticketfields/' + ticketType + '/',
            success: function(data) {
                return cb(null, data);
            },
            error: function(xhr, textStatus, err) {
                return cb(err);
            }
        });
    }
    function onTicketTypeChange () {
        ticketType = $('#id_content_type').val();
        getPossibleFieldNames(ticketType, function(err, data) {
            allowedNames = data;
            rebuildInputs(data);
        });
    }
    function addSelection (sel) {
        if (currentSelection.indexOf(sel) === -1) {
            currentSelection.push(sel);
        }
    }
    function removeSelection (sel) {
        var idx = currentSelection.indexOf(sel);
        if (idx !== -1) {
            currentSelection.splice(idx, 1);
        }
    }
    function onSelectionChange () {
        var val = $(this).val(),
            checked = $(this).is(':checked');
        if (checked) {
            addSelection(val);
        } else {
            removeSelection(val);
        }
    }
    function rebuildInputs (data) {
        var i, len, label, input;
        container.find('div').remove();
        for (i = 0, len = data.length; i < len; i++) {
            label = $('<label>');
            input = $('<input>').attr({
                type: 'checkbox',
                name: '_field',
                value: data[i].name
            });
            if (currentSelection.indexOf(data[i].name) !== -1) {
                input.attr('checked', 'checked');
            }
            label.append(input).append($('<span>').text(data[i].label));
            container.append($('<div>').addClass('editableFieldCheckboxes').append(label));
        }
    }
    $(document).ready(function() {
        var ticketTypeField;
        field = $('#id_editable_fields');
        if (!field.length) {
            return;
        }
        lang = $('html').attr('lang');
        field.hide();
        currentSelection = getSpecifiedFieldNames(field.val());
        container = field.parent();
        form = field.parents('form');
        form.bind('submit', writeBack);
        container.delegate('input', 'change', onSelectionChange);
        ticketTypeField = $('#id_content_type');
        ticketTypeField.bind('change', onTicketTypeChange);
        ticketType = ticketTypeField.val();
        onTicketTypeChange();

    });
})(django.jQuery);
