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


    function fetchToken(csrf) {
        return global.fetchAPIToken(csrf).then(
            (response) => response.token,
            () => null
        );
    }


    function updateTokenDisplay(token) {
        let tokenEl = document.getElementById('token');
        if (token) {
            tokenEl.innerHTML = token;
        } else {
            tokenEl.innerHTML = tokenEl.getAttribute('data-error');
        }
    }


    function showMessage(element, boolean) {
        if (boolean) {
            element.removeAttribute('hidden');
        } else {
            element.setAttribute('hidden', 'true');
        }
    }


    function showTokenRegenSuccessMessage(boolean) {
        let msg = document.getElementById('regen-success');
        showMessage(msg, boolean);
    }


    function showTokenRegenFailureMessage(boolean) {
        let msg = document.getElementById('regen-failure');
        showMessage(msg, boolean);
    }


    function onTokenRegenSuccess() {
        showTokenRegenSuccessMessage(true);
    }


    function onTokenRegenFailure() {
        showTokenRegenFailureMessage(true);
    }


    let form = document.getElementById('user-api-token-form');
    let csrfEl = document.getElementsByName('csrfmiddlewaretoken')[0];
    let confirmText = document.getElementById('regen-confirm-text').innerHTML;

    let token;
    fetchToken(csrfEl.value).then(
        (retval) => {
            token = retval;
            updateTokenDisplay(token);
        }
    );

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        if (confirm(confirmText)) {
            showTokenRegenSuccessMessage(false);
            showTokenRegenFailureMessage(false);
            regenAuthToken(form.action, token).then(
                (response) => {
                    onTokenRegenSuccess();
                    fetchToken(csrfEl.value).then(
                        (retval) => {
                            token = retval;
                            updateTokenDisplay(token);
                        }
                    );
                },
                onTokenRegenFailure
            );
        }
    });

}(this));
