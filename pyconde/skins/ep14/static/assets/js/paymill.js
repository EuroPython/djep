/*global jQuery:true, paymill:true, gettext */
(function($) {
    "use strict";

    $('#payment-form').css({'visibility': 'visible'});
    var mode = $('#payment-form').data('mode') || 'creditcard';

    var backendForm, btn, paymentForm,
        generalError = gettext("An error has occurred. Please try again."),
        nameError = gettext("Invalid name."),
        dateError = gettext("Please verify the expiration date of your credit card."),
        errorMapping = {
            'internal_server_error': generalError,
            'unknown_error': generalError,
            '3ds_cancelled': gettext("3D Secure check has been aborted."),
            'field_invalid_card_number': gettext("Please enter a valid credit card number."),
            'field_invalid_account_number': gettext("Please enter a valid bank account number."),
            'field_invalid_bank_code': gettext("Please enter a valid bank routing number."),
            'field_invalid_card_exp_year': dateError,
            'field_invalid_card_exp_month': dateError,
            'field_invalid_card_exp': gettext("This card is not valid."),
            'field_invalid_card_cvc': gettext("Invalid CVC."),
            'field_invalid_card_holder': nameError,
            'field_invalid_account_holder': nameError,
            'field_invalid_holder': nameError
        };

    function setError(msg) {
        console.log(msg);
        paymentForm.find('.alert').remove();
        paymentForm.prepend($('<p>').text(msg).addClass('alert').addClass('alert-error'));
        paymentForm.data('disabled', false);
        paymentForm.data('spinner').stop();
        paymentForm.data('spinner', null);
    }

    function handleResponse(error, result) {
        if (error) {
            setError(errorMapping[error.apierror] || generalError);
        } else {
            backendForm.append($('<input>').attr({
                'name': 'token',
                'value': result.token,
                'type': 'hidden'
            })).submit();
        }
    }

    $(function() {
        $('#payment-form').on('submit', function(evt) {
            evt.preventDefault();
            var that = $(this),
                ccNumber = that.find('.card-number').val(),
                ccExpYear = that.find('.card-exp-year').val(),
                ccExpMonth = that.find('.card-exp-month').val(),
                ccHolder = that.find('.card-holdername').val(),
                ccCvc = that.find('.card-cvc').val(),
                amount = that.find('.card-amount-int').val(),
                currency = that.find('.card-currency').val(),
                bank = mode === 'elv' ? that.find('.bank').val() : null,
                btn = that.find('button.btn-primary'),
                spinContainer = btn.prepend('<span>'),
                spinner;
            paymentForm = that;
            backendForm  = $('#backend-form');
            if (paymentForm.data('disabled')) {
                return;
            }
            paymentForm.data('disabled', true);
            spinner = new Spinner({
                length: 7,
                radius: 4,
                width: 2,
                left: -60,
                lines: 9,
                color: btn.css('background-color')
            }).spin(spinContainer[0]);
            paymentForm.data('spinner', spinner);

            // Validate the input using PayMill's helper methods
            if (mode === 'creditcard') {
                if (!paymill.validateCardNumber(ccNumber)) {
                    setError(errorMapping.field_invalid_card_number);
                    return;
                }
                if (!paymill.validateExpiry(ccExpMonth, ccExpYear)) {
                    setError(errorMapping.field_invalid_card_exp_year);
                    return;
                }
                if (!paymill.validateCvc(ccCvc)) {
                    setError(errorMapping.field_invalid_card_cvc);
                    return;
                }
            } else {
                if (!paymill.validateAccountNumber(ccNumber)) {
                    setError(errorMapping.field_invalid_account_number);
                    return;
                }
                if (!paymill.validateBankCode(bank)) {
                    setError(errorMapping.field_invalid_bank_code);
                    return;
                }
            }
            if (!ccHolder || !(ccHolder.replace(/\s+/g, ' ')).length) {
                setError(errorMapping.field_invalid_holder);
                return;
            }
            if (mode === 'creditcard') {
                paymill.createToken({
                    number: ccNumber,
                    exp_month: ccExpMonth,
                    exp_year: ccExpYear,
                    cvc: ccCvc,
                    cardholder: ccHolder,
                    amount_int: parseInt(amount, 10),
                    currency: currency
                }, handleResponse);
            } else if (mode === 'elv') {
                paymill.createToken({
                    number: ccNumber,
                    accountholder: ccHolder,
                    bank: bank,
                    amount_int: parseInt(amount, 10),
                    currency: currency
                }, handleResponse);
            }
        });
    });
})(jQuery);
