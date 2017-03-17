interface IDjangoFieldErrors {
    [index: string]: string[];
}

type DjangoGlobalErrors = string[];

type ErrorMessages = {
    global: string[];
    fields: IDjangoFieldErrors;
};

type DjangoErrors = IDjangoFieldErrors | DjangoGlobalErrors;

export function parseJSONError(errorJSON: DjangoErrors): ErrorMessages {
    const result: ErrorMessages = {
        fields: {},
        global: [],
    };

    if (Array.isArray(errorJSON)) {
        result.global = errorJSON;
    } else if (typeof errorJSON === 'object') {
        result.fields = errorJSON;
    }

    return result;
}

type SelectorPairs = Map<string, string[]>;

/**
 * Turns a parsed JSON error into a map of element id's and array of error msgs
 * @param messages
 * @returns {Map<string, string[]>}
 */
export function toIdErrorMap(messages: ErrorMessages): SelectorPairs {
    const result = new Map<string, string[]>();
    result.set('global_error', messages.global);

    const fields = messages.fields;

    Object.keys(fields)
        .map((key) => [key, fields[key]])
        .forEach(([key, value]: [string, string[]]) => {
            result.set('id_' + key, value);
        });

    return result;
}
