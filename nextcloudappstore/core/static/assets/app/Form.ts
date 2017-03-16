interface DjangoFieldErrors {
    [index: string]: Array<string>
}

type DjangoGlobalErrors = Array<string>;

type ErrorMessages = {
    global: Array<string>;
    fields: DjangoFieldErrors;
}

export function parseJSONError(errorJSON: (DjangoFieldErrors | DjangoGlobalErrors)): ErrorMessages {
    const result: ErrorMessages = {
        global: [],
        fields: {}
    };

    if (Array.isArray(errorJSON)) {
        result.global = errorJSON;
    }

    return result;
}
