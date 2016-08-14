(function (window) {
    'use strict';


    function fetchToken(csrf) {
        let request = new Request(
            '/api/v1/token',
            {
                method: 'POST',
                headers: new Headers({
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf,
                }),
                credentials: 'include'
            }
        );
        return fetch(request).then(convertResponse);
    }


    function uploadAppRelease(url, download, checksum, nightly, token) {
        let data = {'download': download, 'nightly': nightly};
        if (checksum) {
            data['checksum'] = checksum;
        }

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
        return fetch(request).then(convertResponse);
    }


    function convertResponse(response) {
        if (response.status >= 200 && response.status < 300) {
            if (response.headers.get('Content-Type') === 'application/json') {
                return response.json();
            } else {
                return response.text();
            }
        }
        return response.json().then(Promise.reject.bind(Promise));
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
    }


    function showSuccessMessage(boolean) {
        let successMsg = document.getElementById('form-success');
        if (boolean) {
            successMsg.removeAttribute('hidden');
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
        Array.from(form.querySelectorAll('input[type=text], input[type=url]')).forEach((el) => {
            el.value = '';
        });
        Array.from(form.querySelectorAll('input[type=checkbox]')).forEach((el) => {
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
    let download = document.getElementById('download');
    let checksum = document.getElementById('checksum');
    let nightly = document.getElementById('nightly');
    let submitButton = document.getElementById('submit');

    // Get the auth token of the currently authenticated user and
    // bind the app release API request to the form submit event.
    fetchToken(csrf.value).then(
        (response) => {
            // User token request successful
            form.addEventListener('submit', (event) => {
                event.preventDefault();
                showSuccessMessage(false);
                disableInputs(form, true);
                buttonState(submitButton, 'loading');
                uploadAppRelease(
                    form.action,
                    download.value,
                    checksum.value,
                    nightly.checked,
                    response.token)
                    .then(onSuccess, onFailure);
            });
        },
        onFailure  // User token request failed
    );


}(this));
