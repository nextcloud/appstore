(function (window) {
    'use strict';

    function sendAppReleaseAPIRequest(download, checksum, nightly, token,
            successCallback, failureCallback) {
        let data = new Object();
        data['download'] = download;
        if (nightly) data['nightly'] = nightly;
        if (checksum) data['checksum'] = checksum;

        let xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/v1/apps/releases', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('Authorization', 'Token ' + token);
        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                clearMessages();
                if (xhr.status == 200 || xhr.status == 201) {
                    successCallback();
                } else {
                    failureCallback(JSON.parse(xhr.response), xhr.status);
                }
            }
        }
        xhr.send(JSON.stringify(data));
    }

    function clearMessages() {
        let msgAreas = Array.from(document.querySelectorAll('[id$="-msg"]'));
        msgAreas.forEach((el) => el.innerHTML = '');
    }

    function printMessages(response, statusCode) {
        let result = 'failure alert-danger';
        if (statusCode == 200 || statusCode == 201) {
            result = 'success alert-success';
        }

        let prop;
        for (prop in response) {
            if (!response.hasOwnProperty(prop)) continue;
            let msg;
            if (typeof response[prop] == 'string') msg = response[prop];
            else if (response[prop] instanceof Array) msg = response[prop].join(' ');
            document.getElementById(prop + '-msg').innerHTML =
                '<div class="alert ' + result + '">' + msg + '</div>';
        }
    }

    function printSuccessMessage() {
        let form = document.getElementById('app-upload-form');
        form.parentNode.innerHTML =
            '<div class="alert success alert-success">App release successfully uploaded.</div>';
    }


    // Get needed values and elements from form.
    let csrf = Array.from(
        document.getElementsByName('csrfmiddlewaretoken'))[0].value;
    let download = document.getElementById('download');
    let checksum = document.getElementById('checksum');
    let nightly = document.getElementById('nightly');
    let submitButton = document.getElementById('submit');

    // Get the auth token of the currently authenticated user and
    // bind the form submit button.
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/v1/token', true);
    xhr.setRequestHeader('X-CSRFToken', csrf);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
            let response = JSON.parse(xhr.response);
            let token = response.token;
            submitButton.addEventListener('click', () => {
                sendAppReleaseAPIRequest(
                    download.value,
                    checksum.value,
                    nightly.checked,
                    token,
                    printSuccessMessage,
                    printMessages);
            });
        }
    }
    xhr.send();

}(this));
