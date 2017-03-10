(function (global) {
    'use strict';

    const Request = global.Request;
    const Headers = global.Headers;
    const fetch = global.fetch;
    const document = global.document;
    const buttonState = global.buttonState;
    const id = global.id;

    function registerApp(url, certificate, signature, token) {
        const data = {
            'certificate': certificate.trim(),
            'signature': signature.trim()
        };

        const request = new Request(
            url,
            {
                method: 'POST',
                headers: new Headers({
                    'Content-Type': 'application/json',
                    'Authorization': 'Token ' + token
                }),
                body: JSON.stringify(data)
            }
        );
        return fetch(request).then(global.convertResponse);
    }


    function clearMessages() {
        const msgAreas = Array.from(document.querySelectorAll('[id$="-msg"]'));
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

            const msgArea = id(key + '-msg');
            const formGroup = msgArea.parentNode;
            const msgP = document.createElement('p');
            const msgTextNode = document.createTextNode(msg);

            msgP.appendChild(msgTextNode);
            msgP.classList.add('text-danger');
            msgArea.innerHTML = '';
            msgArea.appendChild(msgP);
            formGroup.classList.add('has-error');
        });
        window.scrollTo(0, 0);
    }


    function showSuccessMessage(boolean) {
        const successMsg = id('form-success');
        if (boolean) {
            successMsg.removeAttribute('hidden');
            window.scrollTo(0, 0);
        } else {
            successMsg.setAttribute('hidden', 'true');
        }
    }

    function disableInputs(form, boolean) {
        Array.from(form.querySelectorAll('input, button')).forEach((el) => {
            el.disabled = boolean;
        });
    }


    function clearInputs(form) {
        const input = form.querySelectorAll(
            'input[type=text], input[type=url], textarea'
        );
        Array.from(input).forEach((el) => {
            el.value = '';
        });
        const checkbox = form.querySelectorAll('input[type=checkbox]');
        Array.from(checkbox).forEach((el) => {
            el.checked = false;
        });
    }


    function onSuccess() {
        const form = id('app-register-form');
        const submitButton = id('submit');
        clearMessages();
        showSuccessMessage(true);
        clearInputs(form);
        disableInputs(form, false);
        buttonState(submitButton, 'reset');
    }


    function onFailure(response) {
        const form = id('app-register-form');
        const submitButton = id('submit');
        clearMessages();
        printErrorMessages(response);
        disableInputs(form, false);
        buttonState(submitButton, 'reset');
    }


    // Form elements
    const form = id('app-register-form');
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0];
    const certificate = id('id_certificate');
    const signature = id('id_signature');
    const submitButton = id('submit');
    const invalidCertificateMsg = id('invalid-cert-msg')
        .textContent;

    certificate.addEventListener('change', () => {
        const cert = certificate.value.trim();
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
        // Get the auth token of the currently authenticated user.
        global.fetchAPIToken(csrf.value).then(
            (response) => {
                registerApp(
                    form.action,
                    certificate.value,
                    signature.value,
                    response.token)
                    .then(onSuccess, onFailure);
            },
            onFailure // User token request failed
        );
    });

}(this));
