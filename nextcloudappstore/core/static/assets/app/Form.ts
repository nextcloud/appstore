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
    }

    return result;
}
