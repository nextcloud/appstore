interface IDjangoFieldErrors {
    [index: string]: string[];
}

type DjangoGlobalErrors = string[];

type ErrorMessages = {
    global: string[];
    fields: IDjangoFieldErrors;
};

export function parseJSONError(errorJSON: (IDjangoFieldErrors | DjangoGlobalErrors)): ErrorMessages {
    const result: ErrorMessages = {
        fields: {},
        global: [],
    };

    if (Array.isArray(errorJSON)) {
        result.global = errorJSON;
    }

    return result;
}
