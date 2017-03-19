(function (global) {
    'use strict';

    global.fetchAPIToken = function (csrfToken) {
        let request = new Request('/api/v1/token', {
            method: 'POST',
            headers: new Headers({
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            }),
            credentials: 'include'
        });
        return fetch(request).then(global.convertResponse);
    };

    global.convertResponse = function (response) {
        if (response.status >= 200 && response.status < 400) {
            if (response.headers.get('Content-Type') === 'application/json') {
                return response.json();
            } else {
                return response.text();
            }
        }
        return response.json().then(Promise.reject.bind(Promise));
    };

}(this));
