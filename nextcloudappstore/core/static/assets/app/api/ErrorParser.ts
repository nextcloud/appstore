export type FieldErrors = Map<string, string[]>;
export type GlobalErrors = string[];

export type ErrorMessages = {
    global: string[];
    fields: FieldErrors;
};

interface IDjangoFieldErrors {
    [index: string]: string[];
}

type DetailErrors = {
    detail: string;
};

export type DjangoErrors = IDjangoFieldErrors | GlobalErrors | DetailErrors;

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
        // standard error messages
        if (errorJSON.hasOwnProperty('detail')) {
            result.global = [(errorJSON as DetailErrors).detail];
        } else {
            Object.keys(errorJSON).forEach((name) => {
                result.fields.set(
                    name,
                    (errorJSON as IDjangoFieldErrors)[name],
                );
            });
        }
    }

    return result;
}
