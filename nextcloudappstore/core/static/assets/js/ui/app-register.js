(function (global) {
    'use strict';

    function clearMessages() {
        let msgAreas = Array.from(document.querySelectorAll('[id$="-msg"]'));
        msgAreas.forEach((el) => {
            el.innerHTML = '';
            el.parentNode.classList.remove('has-error');
        });
    }

    function printErrorMessages(response) {
        Object.keys(response).forEach((key) => {
            let msg;
            if (typeof response[key] === 'string') {
                msg = response[key];
            } else if (response[key] instanceof Array) {
                msg = response[key].join(' ');
            }

            let msgArea = document.getElementById(key + '-msg');
            let formGroup = msgArea.parentNode;
            let msgP = document.createElement('p');
            let msgTextNode = document.createTextNode(msg);

            msgP.appendChild(msgTextNode);
            msgP.classList.add('text-danger');
            msgArea.innerHTML = '';
            msgArea.appendChild(msgP);
            formGroup.classList.add('has-error');
        });
        window.scrollTo(0, 0);
    }

    function showSuccessMessage(boolean) {
        let successMsg = document.getElementById('form-success');
        if (boolean) {
            successMsg.removeAttribute('hidden');
            window.scrollTo(0, 0);
        } else {
            successMsg.setAttribute('hidden', 'true');
        }
    }

    function buttonState(button, state) {
        switch (state) {
            case 'loading':
                button.setAttribute('data-orig-text', button.innerHTML);
                button.innerHTML = button.getAttribute('data-loading-text');
                break;
            case 'reset':
                if (button.getAttribute('data-orig-text')) {
                    button.innerHTML = button.getAttribute('data-orig-text');
                }
                break;
        }
    }

    function disableInputs(form, boolean) {
        Array.from(form.querySelectorAll('input, button')).forEach((el) => {
            el.disabled = boolean;
        });
    }

    function clearInputs(form) {
        Array.from(form.querySelectorAll('input[type=text], input[type=url], textarea')).forEach((el) => {
            el.value = '';
        });
        Array.from(form.querySelectorAll('input[type=checkbox]')).forEach((el) => {
            el.checked = false;
        });
    }

    function onSuccess() {
        let form = document.getElementById('app-register-form');
        let submitButton = document.getElementById('submit');
        clearMessages();
        showSuccessMessage(true);
        clearInputs(form);
        disableInputs(form, false);
        buttonState(submitButton, 'reset');
    }

    function onFailure(response) {
        let form = document.getElementById('app-register-form');
        let submitButton = document.getElementById('submit');
        clearMessages();
        printErrorMessages(response);
        disableInputs(form, false);
        buttonState(submitButton, 'reset');
    }

    // Form elements
    let form = document.getElementById('app-register-form');
    let csrf = document.getElementsByName('csrfmiddlewaretoken')[0];
    let certificate = document.getElementById('id_certificate');
    let signature = document.getElementById('id_signature');
    let submitButton = document.getElementById('submit');
    let invalidCertificateMsg = document.getElementById('invalid-cert-msg').textContent;

    certificate.addEventListener('change', () => {
        let cert = certificate.value.trim();
        if (!(cert.startsWith('-----BEGIN CERTIFICATE-----') &&
            cert.endsWith('-----END CERTIFICATE-----'))) {
            certificate.setCustomValidity(invalidCertificateMsg);
        } else {
            certificate.setCustomValidity('');
        }
    });

    form.addEventListener('submit', (event) => {
        if (form.checkValidity()) {
            event.preventDefault();
        }
        showSuccessMessage(false);
        disableInputs(form, true);
        buttonState(submitButton, 'loading');

        global.apiRequest({
            url: form.action,
            method: 'POST',
            data: {
                'certificate': certificate.value.trim(),
                'signature': signature.value.trim()
            }
        }, csrf.value)
            .then(onSuccess)
            .catch(onFailure);

    });

}(this));
