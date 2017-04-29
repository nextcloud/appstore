import {DomElementDoesNotExist} from '../dom/DomElementDoesNotExist';
import {queryOrThrow} from '../dom/Facades';
export type FormField = HTMLInputElement | HTMLTextAreaElement |
    HTMLSelectElement;

export class HtmlForm {
    constructor(public readonly form: HTMLFormElement,
                public readonly formGroups: Map<string, Element>,
                public readonly fields: Map<string, FormField>,
                public readonly submit: HTMLInputElement,
                public readonly globalSuccessMessage: HTMLElement,
                public readonly globalErrorMessage: HTMLElement,
                public readonly messages: Map<string, HTMLElement>) {
    }
}

export function isSubmit(field: FormField): boolean {
    return field instanceof HTMLInputElement && field.type === 'submit';
}

/**
 * Returns all non submit fields for a form
 * @param form
 * @returns {Map<string, FormField>}
 */
export function findFormFields(form: HTMLFormElement): Map<string, FormField> {
    const fields = new Map<string, FormField>();
    const formElements = [
        Array.from(form.getElementsByTagName('input')),
        Array.from(form.getElementsByTagName('textarea')),
        Array.from(form.getElementsByTagName('select')),
    ];
    [].concat.apply([], formElements)  // flatten arrays
        .filter((elem: FormField) => !isSubmit(elem))
        .forEach((elem: FormField) => fields.set(elem.name, elem));
    return fields;
}

/**
 * Scans a form for elements and messagefields
 * @param form the actual form
 * @throws DomElementDoesNotExist if required fields are not found
 * @return the form
 */
export function scanForm(form: HTMLFormElement): HtmlForm {
    const fields = findFormFields(form);
    const submit = queryOrThrow('input[type="submit"]', HTMLInputElement, form);
    const globalErrorMsg = queryOrThrow(
        '.global-error-msg', HTMLElement, form,
    );
    const globalSuccessMsg = queryOrThrow(
        '.global-success-msg', HTMLElement, form,
    );
    const msgElements = new Map<string, HTMLElement>();
    const formGroups = new Map<string, Element>();

    fields.forEach((field, name) => {
        if (field.type !== 'hidden') {
            const formGroup = field.closest('.form-group');
            if (formGroup === null) {
                const msg = `No form group found for field ${name}`;
                throw new DomElementDoesNotExist(msg);
            } else {
                formGroups.set(name, formGroup);
            }
            const eMsg = queryOrThrow(`.error-msg-${name}`, HTMLElement, form);
            msgElements.set(name, eMsg);
        }
    });

    return new HtmlForm(
        form, formGroups, fields, submit, globalSuccessMsg, globalErrorMsg,
        msgElements,
    );
}
