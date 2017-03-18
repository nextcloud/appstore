export type FormField = HTMLInputElement | HTMLTextAreaElement |
    HTMLSelectElement | HTMLButtonElement;

export abstract class Form {

    constructor(protected form: HTMLFormElement) {
    }

    protected findFields(): Map<string, FormField> {
        const result = new Map<string, FormField>();
        const fields = [
            Array.from(this.form.getElementsByTagName('input')),
            Array.from(this.form.getElementsByTagName('textarea')),
            Array.from(this.form.getElementsByTagName('select')),
            Array.from(this.form.getElementsByTagName('button')),
        ];
        [].concat.apply([], fields)  // flatten arrays
            .forEach((elem: FormField) => result.set(elem.name, elem));
        return result;
    }

}
