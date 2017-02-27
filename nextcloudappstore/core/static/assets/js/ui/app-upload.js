(function (global) {
    'use strict';

    const Request = global.Request;
    const Headers = global.Headers;
    const fetch = global.fetch;
    const document = global.document;
    const buttonState = global.buttonState;

    function uploadAppRelease(url, download, signature, nightly, token) {
        let data = {
            'download': download,
            'nightly': nightly,
            'signature': signature
        };

        let request = new Request(
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
                msg = response[key].join(', ');
            }

            let msgArea = document.getElementById('detail-msg');
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


    function disableInputs(form, boolean) {
        Array.from(form.querySelectorAll('input, button')).forEach((el) => {
            el.disabled = boolean;
        });
    }


    function clearInputs(form) {
        let input = form.querySelectorAll(
            'input[type=text], input[type=url], textarea'
        );
        Array.from(input).forEach((el) => {
            el.value = '';
        });

        let checkbox = form.querySelectorAll('input[type=checkbox]');
        Array.from(checkbox).forEach((el) => {
            el.checked = false;
        });
    }


    function onSuccess() {
        let form = document.getElementById('app-upload-form');
        let submitButton = document.getElementById('submit');
        clearMessages();
        showSuccessMessage(true);
        clearInputs(form);
        disableInputs(form, false);
        buttonState(submitButton, 'reset');
    }


    function onFailure(response) {
        let form = document.getElementById('app-upload-form');
        let submitButton = document.getElementById('submit');
        clearMessages();
        printErrorMessages(response);
        disableInputs(form, false);
        buttonState(submitButton, 'reset');
    }


    // Form elements
    let form = document.getElementById('app-upload-form');
    let csrf = document.getElementsByName('csrfmiddlewaretoken')[0];
    let download = document.getElementById('id_download');
    let signature = document.getElementById('id_signature');
    let nightly = document.getElementById('id_nightly');
    let submitButton = document.getElementById('submit');

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
                uploadAppRelease(
                    form.action,
                    download.value,
                    signature.value,
                    nightly.checked,
                    response.token)
                    .then(onSuccess, onFailure);
            },
            onFailure // User token request failed
        );
    });

}(this));
