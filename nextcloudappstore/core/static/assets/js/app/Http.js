(function (global, exports) {
    'use strict';

    exports.parseJSONError = (errorJSON) => {
        const result = {
            'global': [],
            'fields': {}
        };

        if (Array.isArray(errorJSON)) {
            result.global = errorJSON;
        }

        return result;
    };

})(window, window.exports = window.exports || {});

