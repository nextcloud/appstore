(function (global, exports) {
    'use strict';

    // shortcuts for unreasonably long DOM methods
    const doc = window.document;
    exports.escapeHtml = (str) => {
        const div = doc.createElement('div');
        div.appendChild(doc.createTextNode(str));
        return div.innerHTML;
    };

})(window, window.exports = window.exports || {});


