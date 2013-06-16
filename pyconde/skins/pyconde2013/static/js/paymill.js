/*global jQuery:true, paymill:true */
(function($) {
    "use strict";

    $('#payment-form').css({'visibility': 'visible'});
    var mode = $('#payment-form').data('mode') || 'creditcard';

    var backendForm, btn, paymentForm,
        errorMapping = {
            'internal_server_error': 'Es ist ein Fehler aufgetreten, bitte versuchen Sie es erneut.',
            'unknown_error': 'Es ist ein Fehler aufgetreten, bitte versuchen Sie es erneut.',
            '3ds_cancelled': '3D-Secure-Check wurde abgebrochen.',
            'field_invalid_card_number': 'Bitte geben Sie eine gültige Kartennummer an.',
            'field_invalid_account_number': 'Bitte geben Sie eine gültige Kontonummer an.',
            'field_invalid_bank_code': 'Bitte geben Sie eine BLZ ein.',
            'field_invalid_card_exp_year': 'Bitte überprüfen Sie das Ablaufdatum ihrer Karte.',
            'field_invalid_card_exp_month': 'Bitte überprüfen Sie das Ablaufdatum ihrer Karte.',
            'field_invalid_card_exp': 'Diese Karte ist nicht gültig.',
            'field_invalid_card_cvc': 'Ungültige Prüfziffer',
            'field_invalid_card_holder': 'Ungültiger Karteninhaber',
            'field_invalid_account_holder': 'Ungültiger Name',
            'field_invalid_holder': 'Ungültiger Name'
        };

    function setError(msg) {
        paymentForm.find('.alert').remove();
        paymentForm.prepend($('<p>').text(msg).addClass('alert').addClass('alert-error'));
        btn.removeAttr('disabled');
    }

    function handleResponse(error, result) {
        if (error) {
            setError(errorMapping[error.apierror] || "Es ist leider ein Fehler aufgetreten. Bitte versuchen Sie es erneut.");
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
                bank = mode === 'elv' ? that.find('.bank').val() : null;
            paymentForm = that;
            backendForm  = $('#backend-form'),
            btn = that.find('button');
            btn.attr('disabled', 'disabled');

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
                    amount: amount,
                    currency: currency
                }, handleResponse);
            } else if (mode === 'elv') {
                paymill.createToken({
                    number: ccNumber,
                    accountholder: ccHolder,
                    bank: bank,
                    amount: amount,
                    currency: currency
                }, handleResponse);
            }
        });
    });
})(jQuery);
