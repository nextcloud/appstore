import {IErrorMessages, parseJSONError} from '../api/ErrorParser';
import {Translator} from '../l10n/Translator';
import {Maybe} from '../Utils';
import {FormField, HtmlForm} from './HtmlForm';
import {NoValidatorBound} from './NoValidatorBound';
import {Invalid} from './validators/Invalid';
import {IValidator} from './validators/IValidator';

export abstract class AjaxForm<T> {

    constructor(private readonly form: HtmlForm,
                private readonly validators: Map<string, IValidator[]>,
                protected readonly translator: Translator) {
    }

    public bindListeners() {
        this.bindValidators();
        this.bindSubmit();
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
                const result = validator.validate(field.value.trim());
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

    protected bindSubmit() {
        this.form.form.addEventListener('submit', (event) => {
            this.onSubmit(event);
        });
    }

    protected abstract submit(form: HtmlForm): Promise<T>;

    protected onSubmit(event: Event) {
        if (this.form.form.checkValidity()) {
            // submit form with Ajax
            event.preventDefault();
            this.clearFormFieldErrors();
            this.lockFields();
            this.clearMessages();

            this.submit(this.form)
                .then(() => {
                    const msg = this.translator.get('msg-form-success');
                    this.showSuccessMessage(msg);
                    this.form.form.reset();
                    return Promise.resolve.bind(Promise);
                }, (error) => {
                    this.showErrorMessages(parseJSONError(error));
                    return Promise.resolve.bind(Promise);
                })
                .then(() => {
                    this.unlockFields();
                })
                .catch(() => this.unlockFields());
        }
    }

    protected showSuccessMessage(msg?: string) {
        const globalSuccessMessage = this.form.globalSuccessMessage;
        if (globalSuccessMessage.parentElement !== null && msg !== undefined &&
            msg !== '') {
            globalSuccessMessage.innerText = msg;
            globalSuccessMessage.hidden = false;
        }
    }

    protected clearFormFieldErrors() {
        this.form.formGroups
            .forEach((elem) => {
                elem.classList.remove('has-error', 'has-feedback');
            });
    }

    protected showErrorMessages(messages: IErrorMessages) {
        // FIXME: this will put all messages into one element
        // would be nicer if instead we just copied and inserted templated
        // elements
        messages.fields.forEach((list, name) => {
            const msg = this.form.messages.get(name);
            if (msg !== undefined && this.hasMessages(list) &&
                msg.parentElement !== null) {
                msg.parentElement.hidden = false;
                msg.innerText = list.join('\n');
                new Maybe(this.form.formGroups.get(name))
                    .ifPresent((elem) => {
                        elem.classList.add('has-feedback', 'has-error');
                    });
            }
        });
        const globalErrorMessage = this.form.globalErrorMessage;
        if (globalErrorMessage.parentElement !== null &&
            this.hasMessages(messages.global)) {
            globalErrorMessage.hidden = false;
            globalErrorMessage.innerText = messages.global.join('\n');
        }
    }

    protected hasMessages(messages: string[]): boolean {
        return messages.join('').trim() !== '';
    }

    protected clearMessages() {
        this.form.messages.forEach((elem) => {
            elem.innerText = '';
            if (elem.parentElement !== null) {
                elem.parentElement.hidden = true;
            }
        });
        const globalErrorMessage = this.form.globalErrorMessage;
        if (globalErrorMessage.parentElement !== null) {
            globalErrorMessage.innerText = '';
            globalErrorMessage.hidden = true;
        }
        const globalSuccessMessage = this.form.globalSuccessMessage;
        if (globalSuccessMessage.parentElement !== null) {
            globalSuccessMessage.innerText = '';
            globalSuccessMessage.hidden = true;
        }
    }

    protected lockFields() {
        this.form.fields.forEach((field) => field.disabled = true);
        this.form.submit.classList.add('btn-loading');
        this.form.submit.disabled = true;
    }

    protected unlockFields() {
        this.form.fields.forEach((field) => field.disabled = false);
        this.form.submit.classList.remove('btn-loading');
        this.form.submit.disabled = false;
    }

    protected findCsrfToken(): string {
        const field = this.form.fields.get('csrfmiddlewaretoken');
        if (field === undefined) {
            return '';
        } else {
            return field.value;
        }
    }
}
