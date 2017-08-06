import {apiRequest, HttpMethod} from '../../api/Request';
import {AjaxForm} from '../../forms/AjaxForm';
import {FormField, HtmlForm} from '../../forms/HtmlForm';
import {IValidator} from '../../forms/validators/IValidator';
import {Translator} from '../../l10n/Translator';
import {Maybe} from '../../Utils';

export class AppRegisterForm extends AjaxForm<object> {
    private readonly url: string;

    constructor(form: HtmlForm,
                validators: Map<string, IValidator[]>,
                translator: Translator) {
        super(form, validators, translator);
        this.url = form.form.action;
    }

    protected submit(form: HtmlForm): Promise<object> {
        const values = form.fields;
        const certificate = new Maybe<FormField>(values.get('certificate'));
        const signature = new Maybe<FormField>(values.get('signature'));
        const data = {
            data: {
                certificate: certificate
                    .map((field) => field.value.trim())
                    .orElse(''),
                signature: signature
                    .map((field) => field.value.trim())
                    .orElse(''),
            },
            method: HttpMethod.POST,
            url: this.url,
        };
        return apiRequest(data, this.findCsrfToken());
    }

}
