(function (global) {
    'use strict';

    function regenAuthToken(url, api_token) {
        let request = new Request(
            url,
            {
                method: 'POST',
                headers: new Headers({
                    'Content-Type': 'application/json',
                    'Authorization': 'Token ' + api_token
                }),
            }
        );
        return fetch(request).then(global.convertResponse);
    };


    function showElement(element, boolean) {
        if (boolean) {
            element.removeAttribute('hidden');
        } else {
            element.setAttribute('hidden', 'true');
        }
    }


    function showTokenFetchFailureMessage(boolean) {
        let msg = document.getElementById('token-failure');
        let paragraphs = Array.from(document.querySelectorAll('#tokenSection p'));
        showElement(msg, boolean);
        paragraphs.forEach((p) => showElement(p, !boolean));
    }


    function showTokenRegenSuccessMessage(boolean) {
        let msg = document.getElementById('regen-success');
        showElement(msg, boolean);
    }


    function showTokenRegenFailureMessage(boolean) {
        let msg = document.getElementById('regen-failure');
        showElement(msg, boolean);
    }


    function updateTokenDisplay(token) {
        let tokenEl = document.getElementById('token');
        tokenEl.innerHTML = token;
    }


    function updateToken(csrf) {
        global.fetchAPIToken(csrf).then(
            (response) => {
                updateTokenDisplay(response.token);
                showTokenFetchFailureMessage(false);
            },
            showTokenFetchFailureMessage(true)
        );
    }


    function onTokenRegenSuccess(response) {
        showTokenRegenSuccessMessage(true);
        showTokenFetchFailureMessage(false);
        updateTokenDisplay(response.token);
    }


    function onTokenRegenFailure() {
        showTokenRegenFailureMessage(true);
    }


    let form = document.getElementById('api-token-regen-form');
    let csrfEl = document.getElementsByName('csrfmiddlewaretoken')[0];
    let tokenEl = document.getElementById('token');
    let confirmText = document.getElementById('regen-confirm-text').innerHTML;

    updateToken(csrfEl.value);

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        if (confirm(confirmText)) {
            showTokenRegenSuccessMessage(false);
            showTokenRegenFailureMessage(false);
            regenAuthToken(form.action, tokenEl.innerHTML).then(
                (response) => onTokenRegenSuccess(response),
                onTokenRegenFailure
            );
        }
    });

}(this));
