import {Translator} from '../l10n/Translator';
import {FormField, HtmlForm} from './HtmlForm';
import {NoValidatorBound} from './NoValidatorBound';
import {Invalid} from './validators/Invalid';
import {IValidator} from './validators/IValidator';

export class AjaxForm {

    constructor(private form: HtmlForm,
                private validators: Map<string, IValidator[]>,
                private translator: Translator) {
        this.bindValidators();
    }

    protected bindValidators() {
        this.validators.forEach((validatorList: IValidator[], name: string) => {
            const field = this.form.fields.get(name);
            if (field === undefined) {
                throw new NoValidatorBound(`No field found with ${name}`);
            } else {
                this.bindFieldValidators(field, validatorList);

            }
        });
    }

    protected bindFieldValidators(field: FormField,
                                  validatorList: IValidator[]) {
        field.addEventListener('change', () => {
            const messages: string[] = [];
            validatorList.forEach((validator: IValidator) => {
                const result = validator.validate(field.value);
                if (result instanceof Invalid) {
                    messages.push(this.translator.get(result.errorMsgId));
                }
            });
            if (messages.length > 0) {
                field.setCustomValidity(messages.join('\n'));
            } else {
                field.setCustomValidity('');
            }
        });
    }

    protected submit(values: Map<string, string>): Promise<string> {
        return Promise.resolve.bind(Promise);
    }

    protected onSubmit(event: Event) {
        if (this.form.form.checkValidity()) {
            // submit form with Ajax
            event.preventDefault();

            this.lockFields();
            this.clearMessages();

            const values = new Map<string, string>();
            this.form.fields.forEach((field, name) => {
                values.set(name, field.value.trim());
            });

            this.submit(values)
                .then(() => {
                    this.unlockFields();
                    this.clearFields();
                })
                .catch(() => this.unlockFields());
        }
    }

    protected clearMessages() {
        this.form.messages.forEach((elem) => {
            elem.innerText = '';
            elem.hidden = true;
        });
        this.form.globalMessage.innerText = '';
        this.form.globalMessage.hidden = true;
    }

    protected clearFields() {
        this.form.fields.forEach((field) => {
            if (!field.dataset.preventClear) {
                field.value = '';
            }
        });
    }

    protected lockFields() {
        this.form.fields.forEach((field) => field.disabled = true);
        this.form.submit.classList.add('loading');
    }

    protected unlockFields() {
        this.form.fields.forEach((field) => field.disabled = false);
        this.form.submit.classList.remove('loading');
    }
}
