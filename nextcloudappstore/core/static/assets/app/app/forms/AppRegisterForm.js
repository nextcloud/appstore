import { apiRequest, HttpMethod } from '../../api/Request';
import { AjaxForm } from '../../forms/AjaxForm';
import { Maybe } from '../../Utils';
export class AppRegisterForm extends AjaxForm {
    constructor(form, validators, translator) {
        super(form, validators, translator);
        this.url = form.form.action;
    }
    submit(form) {
        const values = form.fields;
        const certificate = new Maybe(values.get('certificate'));
        const signature = new Maybe(values.get('signature'));
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
//# sourceMappingURL=AppRegisterForm.js.map