(function (global) {
    'use strict';

    function showElement(element, show) {
        if (show) {
            element.removeAttribute('hidden');
        } else {
            element.setAttribute('hidden', 'true');
        }
    }

    function showTokenFetchFailureMessage() {
        let msg = document.getElementById('token-failure');
        let elementsToHide = Array.from(document.querySelectorAll('#tokenSection .hide-on-token-failure'));
        showElement(msg, true);
        elementsToHide.forEach((el) => showElement(el, false));
    }

    function showTokenRegenSuccessMessage(show) {
        let msg = document.getElementById('regen-success');
        showElement(msg, show);
    }

    function showTokenRegenFailureMessage(show) {
        let msg = document.getElementById('regen-failure');
        showElement(msg, show);
    }

    function updateTokenDisplay(token) {
        let tokenEl = document.getElementById('token');
        tokenEl.innerHTML = token;
    }

    function updateToken(csrf) {
        global.fetchToken(csrf).then(
            updateTokenDisplay,
            showTokenFetchFailureMessage
        );
    }

    function onSuccess(response) {
        showTokenRegenSuccessMessage(true);
        updateTokenDisplay(response.token);
    }

    function onFailure() {
        showTokenRegenFailureMessage(true);
    }

    let form = document.getElementById('api-token-regen-form');
    let csrfEl = document.getElementsByName('csrfmiddlewaretoken')[0];
    let confirmText = document.getElementById('regen-confirm-text').innerHTML;

    updateToken(csrfEl.value);

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        if (confirm(confirmText)) {
            showTokenRegenSuccessMessage(false);
            showTokenRegenFailureMessage(false);
            global.apiRequest({
                url: form.action,
                method: 'POST'
            }, csrfEl.value)
                .then(onSuccess)
                .catch(onFailure);
        }
    });

}(this));
