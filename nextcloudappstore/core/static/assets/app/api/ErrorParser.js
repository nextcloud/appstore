export function parseJSONError(errorJSON) {
    const result = {
        fields: new Map(),
        global: [],
    };
    if (Array.isArray(errorJSON)) {
        result.global = errorJSON;
    }
    else if (typeof errorJSON === 'object') {
        if (errorJSON.hasOwnProperty('detail')) {
            result.global = [errorJSON.detail];
        }
        else {
            Object.keys(errorJSON).forEach((name) => {
                result.fields.set(name, errorJSON[name]);
            });
        }
    }
    return result;
}
//# sourceMappingURL=ErrorParser.js.map