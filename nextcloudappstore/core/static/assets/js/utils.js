(function (global) {
    'use strict';

    global.noreferrerLinks = function (html) {
        let parser = new DOMParser();
        let doc = parser.parseFromString(html, 'text/html');
        Array.from(doc.getElementsByTagName('a')).forEach(link => link.rel = 'noopener noreferrer');
        return doc.body.innerHTML;
    };
}(this));
