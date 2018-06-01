import { apiRequest, HttpMethod } from '../../api/Request';
import { AjaxForm } from '../../forms/AjaxForm';
import { Maybe } from '../../Utils';
export class AppUploadForm extends AjaxForm {
    constructor(form, translator) {
        super(form, new Map(), translator);
        this.url = form.form.action;
    }
    submit(form) {
        const values = form.fields;
        const download = new Maybe(values.get('download'));
        const signature = new Maybe(values.get('signature'));
        const nightly = new Maybe(values.get('nightly'));
        const data = {
            data: {
                download: download
                    .map((field) => field.value.trim())
                    .orElse(''),
                nightly: nightly
                    .map((field) => {
                    return field instanceof HTMLInputElement &&
                        field.checked;
                })
                    .orElse(false),
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
//# sourceMappingURL=AppUploadForm.js.map