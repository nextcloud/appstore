(function (global) {
    'use strict';

    const DOMParser = global.DOMParser;
    const Request = global.Request;
    const Headers = global.Headers;
    const fetch = global.fetch;
    const document = global.document;

    global.noReferrerLinks = function (html) {
        let parser = new DOMParser();
        let doc = parser.parseFromString(html, 'text/html');
        Array.from(doc.getElementsByTagName('a'))
            .forEach(link => link.rel = 'noopener noreferrer');
        return doc.body.innerHTML;
    };

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

    global.escapeHtml = function (str) {
        let div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    };

    global.id = (selector) => global.document.getElementById(selector);

    global.buttonState = (button, state) => {
        if (state === 'loading') {
            button.setAttribute('data-orig-text', button.innerHTML);
            button.innerHTML = button.getAttribute('data-loading-text');
        } else {
            if (button.getAttribute('data-orig-text')) {
                button.innerHTML = button.getAttribute('data-orig-text');
            }
        }
    };

    global.metaVal = (key) => {
        return document.querySelector(`meta[name="${key}"]`).content;
    };

}(this));
