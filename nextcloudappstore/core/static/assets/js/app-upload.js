(function (window) {
    'use strict';


    function apiRequestToken(csrf) {
        var request = new Request(
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

        return fetch(request).then((response) => {
            var json = response.json();
            if (response.status == 200) {
                return json;
            } else {
                return json.then(Promise.reject.bind(Promise));
            }
        });
    }


    function apiRequestAppRelease(url, download, checksum, nightly, token) {
        var data = {'download': download};
        if (nightly) {
            data['nightly'] = nightly;
        }
        if (checksum) {
            data['checksum'] = checksum;
        }

        var request = new Request(
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
            if (response.status == 200 || response.status == 201) {
                return response;
            } else {
                return response.json().then(Promise.reject.bind(Promise));
            }
        });
    }


    function clearMessages() {
        var msgAreas = Array.from(document.querySelectorAll('[id$="-msg"]'));
        msgAreas.forEach((el) => el.innerHTML = '');
    }


    function printErrorMessages(response) {
        clearMessages();
        Object.keys(response).forEach((key) => {
            var msg;
            if (typeof response[key] == 'string') {
                msg = response[key];
            } else if (response[key] instanceof Array) {
                msg = response[key].join(' ');
            }

            var msgArea = document.getElementById(key + '-msg');
            var msgDiv = document.createElement('div');
            var msgP = document.createElement('p');
            var msgTextNode = document.createTextNode(msg);

            msgP.appendChild(msgTextNode);
            msgDiv.appendChild(msgP);
            msgDiv.classList.add('alert', 'alert-danger', 'failure');
            msgArea.innerHTML = '';
            msgArea.appendChild(msgDiv);
        });
    }


    function printSuccessMessage() {
        var form = document.getElementById('app-upload-form');
        var successMsg = document.getElementById('form-success');
        form.remove();
        successMsg.removeAttribute('hidden');
    }


    // Get needed values and elements from form.
    let form = document.getElementById('app-upload-form');
    let url = form.action;
    let csrf = Array.from(
        document.getElementsByName('csrfmiddlewaretoken'))[0].value;
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
                .then(
                    () => printSuccessMessage(), // App release request successful
                    (response) => printErrorMessages(response) // App release request failed
                );
        });
    }, (response) => {
        // User token request failed
        printErrorMessages(response);
    });

}(this));
