import {queryOrThrow} from '../dom/Facades';
export type FormField = HTMLInputElement | HTMLTextAreaElement |
    HTMLSelectElement;

export class HtmlForm {
    public form: HTMLFormElement;
    public fields: Map<string, FormField>;
    public submit: HTMLInputElement;
    public globalMessage: HTMLElement;
    public messages: Map<string, HTMLElement>;

    constructor(form: HTMLFormElement, fields: Map<string, FormField>,
                submit: HTMLInputElement, globalMessage: HTMLElement,
                messages: Map<string, HTMLElement>) {
        this.form = form;
        this.fields = fields;
        this.submit = submit;
        this.globalMessage = globalMessage;
        this.messages = messages;
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
    const submit = queryOrThrow<HTMLInputElement>('input[type="submit"]', form);
    const globalMsgElement = queryOrThrow<HTMLElement>('.global-msg', form);
    const msgElements = new Map<string, HTMLElement>();

    fields.forEach((field, name) => {
        if (field.type !== 'hidden') {
            msgElements.set(name, queryOrThrow(`.msg-${name}`, form));
        }
    });

    return new HtmlForm(form, fields, submit, globalMsgElement, msgElements);
}
