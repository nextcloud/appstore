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
        msgAreas.forEach((el) => el.innerHTML = '');
    }


    function printErrorMessages(response) {
        clearMessages();
        Object.keys(response).forEach((key) => {
            let msg;
            if (typeof response[key] === 'string') {
                msg = response[key];
            } else if (response[key] instanceof Array) {
                msg = response[key].join(' ');
            }

            let msgArea = document.getElementById(key + '-msg');
            let msgDiv = document.createElement('div');
            let msgP = document.createElement('p');
            let msgTextNode = document.createTextNode(msg);

            msgP.appendChild(msgTextNode);
            msgDiv.appendChild(msgP);
            msgDiv.classList.add('alert', 'alert-danger', 'failure');
            msgArea.innerHTML = '';
            msgArea.appendChild(msgDiv);
        });
    }


    function printSuccessMessage() {
        clearMessages();
        let form = document.getElementById('app-upload-form');
        let successMsg = document.getElementById('form-success');
        form.remove();
        successMsg.removeAttribute('hidden');
    }


    // Form elements
    let form = document.getElementById('app-upload-form');
    let csrf = document.getElementsByName('csrfmiddlewaretoken')[0];
    let download = document.getElementById('download');
    let checksum = document.getElementById('checksum');
    let nightly = document.getElementById('nightly');

    // Get the auth token of the currently authenticated user and
    // bind the app release API request to the form submit event.
    fetchToken(csrf.value).then(
        (response) => {
            // User token request successful
            form.addEventListener('submit', (event) => {
                event.preventDefault();
                uploadAppRelease(
                    form.action,
                    download.value,
                    checksum.value,
                    nightly.checked,
                    response.token)
                    .then(printSuccessMessage, printErrorMessages);
            });
        },
        printErrorMessages  // User token request failed
    );


}(this));
