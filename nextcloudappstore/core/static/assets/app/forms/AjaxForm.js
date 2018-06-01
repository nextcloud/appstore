import { parseJSONError } from '../api/ErrorParser';
import { Maybe } from '../Utils';
import { NoValidatorBound } from './NoValidatorBound';
import { Invalid } from './validators/Invalid';
export class AjaxForm {
    constructor(form, validators, translator) {
        this.form = form;
        this.validators = validators;
        this.translator = translator;
    }
    bindListeners() {
        this.bindValidators();
        this.bindSubmit();
    }
    bindValidators() {
        this.validators.forEach((validatorList, name) => {
            const field = this.form.fields.get(name);
            if (field === undefined) {
                throw new NoValidatorBound(`No field found with ${name}`);
            }
            else {
                this.bindFieldValidators(field, validatorList);
            }
        });
    }
    bindFieldValidators(field, validatorList) {
        field.addEventListener('change', () => {
            const messages = [];
            validatorList.forEach((validator) => {
                const result = validator.validate(field.value.trim());
                if (result instanceof Invalid) {
                    messages.push(this.translator.get(result.errorMsgId));
                }
            });
            if (messages.length > 0) {
                field.setCustomValidity(messages.join('\n'));
            }
            else {
                field.setCustomValidity('');
            }
        });
    }
    bindSubmit() {
        this.form.form.addEventListener('submit', (event) => {
            this.onSubmit(event);
        });
    }
    onSubmit(event) {
        if (this.form.form.checkValidity()) {
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
    showSuccessMessage(msg) {
        const globalSuccessMessage = this.form.globalSuccessMessage;
        if (globalSuccessMessage.parentElement !== null && msg !== undefined &&
            msg !== '') {
            globalSuccessMessage.innerText = msg;
            globalSuccessMessage.hidden = false;
        }
    }
    clearFormFieldErrors() {
        this.form.formGroups
            .forEach((elem) => {
            elem.classList.remove('has-error', 'has-feedback');
        });
    }
    showErrorMessages(messages) {
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
    hasMessages(messages) {
        return messages.join('').trim() !== '';
    }
    clearMessages() {
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
    lockFields() {
        this.form.fields.forEach((field) => field.disabled = true);
        this.form.submit.classList.add('btn-loading');
        this.form.submit.disabled = true;
    }
    unlockFields() {
        this.form.fields.forEach((field) => field.disabled = false);
        this.form.submit.classList.remove('btn-loading');
        this.form.submit.disabled = false;
    }
    findCsrfToken() {
        const field = this.form.fields.get('csrfmiddlewaretoken');
        if (field === undefined) {
            return '';
        }
        else {
            return field.value;
        }
    }
}
//# sourceMappingURL=AjaxForm.js.map