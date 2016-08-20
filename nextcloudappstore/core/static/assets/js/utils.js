(function (global) {
    'use strict';

    global.noreferrerLinks = function (html) {
        let parser = new DOMParser();
        let doc = parser.parseFromString(html, 'text/html');
        Array.from(doc.getElementsByTagName('a')).forEach(link => link.rel = 'noopener noreferrer');
        return doc.body.innerHTML;
    };


    global.fetchAPIToken = function (csrf) {
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
        return fetch(request).then(global.convertResponse);
    };


    global.convertResponse = function (response) {
        if (response.status >= 200 && response.status < 300) {
            if (response.headers.get('Content-Type') === 'application/json') {
                return response.json();
            } else {
                return response.text();
            }
        }
        return response.json().then(Promise.reject.bind(Promise));
    }

}(this));
