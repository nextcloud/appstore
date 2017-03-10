(function (global) {
    'use strict';

    const Request = global.Request;
    const Headers = global.Headers;
    const fetch = global.fetch;
    const document = global.document;
    const buttonState = global.buttonState;
    const id = global.id;

    function uploadAppRelease(url, download, signature, nightly, token) {
        const data = {
            'download': download,
            'nightly': nightly,
            'signature': signature
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
                msg = response[key].join(', ');
            }

            const msgArea = id('detail-msg');
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


    function showSuccessMessage(isShowSuccessMsg) {
        const successMsg = id('form-success');
        if (isShowSuccessMsg) {
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
        const form = id('app-upload-form');
        const submitButton = id('submit');
        clearMessages();
        showSuccessMessage(true);
        clearInputs(form);
        disableInputs(form, false);
        buttonState(submitButton, 'reset');
    }


    function onFailure(response) {
        const form = id('app-upload-form');
        const submitButton = id('submit');
        clearMessages();
        printErrorMessages(response);
        disableInputs(form, false);
        buttonState(submitButton, 'reset');
    }


    // Form elements
    const form = id('app-upload-form');
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0];
    const download = id('id_download');
    const signature = id('id_signature');
    const nightly = id('id_nightly');
    const submitButton = id('submit');

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
