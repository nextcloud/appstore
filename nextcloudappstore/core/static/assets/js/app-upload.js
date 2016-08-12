(function (window) {
    'use strict';


    function apiRequestToken(csrf) {
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
        return fetch(request).then((response) => response.json());
    }


    function apiRequestAppRelease(url, download, checksum, nightly, token) {
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

        return fetch(request).then((response) => {
            if (response.status === 200 || response.status === 201) {
                return response;
            } else {
                return response.json().then(Promise.reject.bind(Promise));
            }
        });
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


    // Get needed values and elements from form.
    let form = document.getElementById('app-upload-form');
    let url = form.action;
    let csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let download = document.getElementById('download');
    let checksum = document.getElementById('checksum');
    let nightly = document.getElementById('nightly');

    // Get the auth token of the currently authenticated user and
    // bind the app release API request to the form submit event.
    apiRequestToken(csrf).then((response) => {
        // User token request successful
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            apiRequestAppRelease(
                url,
                download.value,
                checksum.value,
                nightly.checked,
                response.token)
                .then(printSuccessMessage, printErrorMessages);
        });
    }, (response) => {
        // User token request failed
        printErrorMessages(response);
    });

}(this));
