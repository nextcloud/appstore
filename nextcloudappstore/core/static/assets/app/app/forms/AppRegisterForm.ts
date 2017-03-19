import {FormField, HtmlForm} from '../../forms/HtmlForm';
import {NoValidatorBound} from '../../forms/NoValidatorBound';
import {Invalid} from '../../forms/validators/Invalid';
import {IValidator} from '../../forms/validators/IValidator';
import {Translator} from '../../l10n/Translator';

export class AppRegisterForm {

    constructor(private form: HtmlForm,
                private validators: Map<string, IValidator[]>,
                private translator: Translator) {
        this.bindValidators();
    }

    private bindValidators() {
        this.validators.forEach((validatorList: IValidator[], name: string) => {
            const field = this.form.fields.get(name);
            if (field === undefined) {
                throw new NoValidatorBound(`No field found with ${name}`);
            } else {
                this.bindFieldValidators(field, validatorList);

            }
        });
    }

    private bindFieldValidators(field: FormField, validatorList: IValidator[]) {
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

    private onSubmit(event: Event) {
        if (this.form.form.checkValidity()) {
            event.preventDefault();
        }
    }
}
