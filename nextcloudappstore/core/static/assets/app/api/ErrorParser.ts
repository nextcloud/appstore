export type FieldErrors = Map<string, string[]>;
export type GlobalErrors = string[];

export interface IErrorMessages {
    global: string[];
    fields: FieldErrors;
}

interface IDjangoFieldErrors {
    [index: string]: string[];
}

export interface IDetailErrors {
    detail: string;
}

export type DjangoErrors = IDjangoFieldErrors | GlobalErrors | IDetailErrors;

/**
 * Parses a JSON error from a Django Restframework API
 * @param errorJSON
 * @returns {IErrorMessages}
 */
export function parseJSONError(errorJSON: DjangoErrors): IErrorMessages {
    const result: IErrorMessages = {
        fields: new Map<string, string[]>(),
        global: [],
    };

    if (Array.isArray(errorJSON)) {
        result.global = errorJSON;
    } else if (typeof errorJSON === 'object') {
        // standard error messages
        if (errorJSON.hasOwnProperty('detail')) {
            result.global = [(errorJSON as IDetailErrors).detail];
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
