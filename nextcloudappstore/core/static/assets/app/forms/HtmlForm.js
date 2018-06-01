import { DomElementDoesNotExist } from '../dom/DomElementDoesNotExist';
import { queryOrThrow } from '../dom/Facades';
export class HtmlForm {
    constructor(form, formGroups, fields, submit, globalSuccessMessage, globalErrorMessage, messages) {
        this.form = form;
        this.formGroups = formGroups;
        this.fields = fields;
        this.submit = submit;
        this.globalSuccessMessage = globalSuccessMessage;
        this.globalErrorMessage = globalErrorMessage;
        this.messages = messages;
    }
}
export function isSubmit(field) {
    return field instanceof HTMLInputElement && field.type === 'submit';
}
export function findFormFields(form) {
    const fields = new Map();
    const formElements = [
        Array.from(form.getElementsByTagName('input')),
        Array.from(form.getElementsByTagName('textarea')),
        Array.from(form.getElementsByTagName('select')),
    ];
    [].concat.apply([], formElements)
        .filter((elem) => !isSubmit(elem))
        .forEach((elem) => fields.set(elem.name, elem));
    return fields;
}
export function scanForm(form) {
    const fields = findFormFields(form);
    const submit = queryOrThrow('input[type="submit"]', HTMLInputElement, form);
    const globalErrorMsg = queryOrThrow('.global-error-msg', HTMLElement, form);
    const globalSuccessMsg = queryOrThrow('.global-success-msg', HTMLElement, form);
    const msgElements = new Map();
    const formGroups = new Map();
    fields.forEach((field, name) => {
        if (field.type !== 'hidden') {
            const formGroup = field.closest('.form-group');
            if (formGroup === null) {
                const msg = `No form group found for field ${name}`;
                throw new DomElementDoesNotExist(msg);
            }
            else {
                formGroups.set(name, formGroup);
            }
            const eMsg = queryOrThrow(`.error-msg-${name}`, HTMLElement, form);
            msgElements.set(name, eMsg);
        }
    });
    return new HtmlForm(form, formGroups, fields, submit, globalSuccessMsg, globalErrorMsg, msgElements);
}
//# sourceMappingURL=HtmlForm.js.map