export type FieldErrors = Map<string, string[]>;
export type GlobalErrors = string[];

export type ErrorMessages = {
    global: string[];
    fields: FieldErrors;
};

interface IDjangoFieldErrors {
    [index: string]: string[];
}

export type DjangoErrors = IDjangoFieldErrors | GlobalErrors;

/**
 * Parses a JSON error from a Django Restframework API
 * @param errorJSON
 * @returns {ErrorMessages}
 */
export function parseJSONError(errorJSON: DjangoErrors): ErrorMessages {
    const result: ErrorMessages = {
        fields: new Map<string, string[]>(),
        global: [],
    };

    if (Array.isArray(errorJSON)) {
        result.global = errorJSON;
    } else if (typeof errorJSON === 'object') {
        Object.keys(errorJSON).forEach((name) => {
            result.fields.set(name, errorJSON[name]);
        });
    }

    return result;
}
