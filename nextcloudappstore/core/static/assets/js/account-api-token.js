(function (global) {
    'use strict';

    const confirm = global.confirm;
    const Request = global.Request;
    const Headers = global.Headers;
    const fetch = global.fetch;
    const document = global.document;
    const id = global.id;

    function regenAuthToken(url, api_token) {
        const request = new Request(
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
    }

    function showElement(element, show) {
        if (show) {
            element.removeAttribute('hidden');
        } else {
            element.setAttribute('hidden', 'true');
        }
    }


    function showTokenFetchFailureMessage() {
        const msg = document.getElementById('token-failure');
        const hideSelector = '#tokenSection .hide-on-token-failure';
        const elementsToHide = document.querySelectorAll(hideSelector);
        showElement(msg, true);
        Array.from(elementsToHide)
            .forEach((el) => showElement(el, false));
    }


    function showTokenRegenSuccessMessage(show) {
        const msg = document.getElementById('regen-success');
        showElement(msg, show);
    }


    function showTokenRegenFailureMessage(show) {
        const msg = document.getElementById('regen-failure');
        showElement(msg, show);
    }


    function updateTokenDisplay(token) {
        const tokenEl = document.getElementById('token');
        tokenEl.innerHTML = token;
    }


    function updateToken(csrf) {
        global.fetchAPIToken(csrf).then(
            (response) => updateTokenDisplay(response.token),
            showTokenFetchFailureMessage
        );
    }


    function onTokenRegenSuccess(response) {
        showTokenRegenSuccessMessage(true);
        updateTokenDisplay(response.token);
    }


    function onTokenRegenFailure() {
        showTokenRegenFailureMessage(true);
    }


    const form = id('api-token-regen-form');
    const csrfEl = document.getElementsByName('csrfmiddlewaretoken')[0];
    const tokenEl = id('token');
    const confirmText = id('regen-confirm-text').innerHTML;

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
