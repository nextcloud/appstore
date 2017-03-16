(function (global, exports) {
    'use strict';

    // shortcuts for unreasonably long DOM methods
    const doc = window.document;
    exports.dom.id = doc.getElementById.bind(doc);
    exports.dom.selectAll = doc.querySelectorAll.bind(doc);
    exports.dom.select = doc.querySelector.bind(doc);

})(window, window.exports = window.exports || {});

