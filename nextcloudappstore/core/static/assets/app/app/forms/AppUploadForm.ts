import {apiRequest, HttpMethod} from '../../api/Request';
import {AjaxForm} from '../../forms/AjaxForm';
import {FormField, HtmlForm} from '../../forms/HtmlForm';
import {Translator} from '../../l10n/Translator';
import {Maybe} from '../../Utils';

export class AppUploadForm extends AjaxForm<object> {
    private readonly url: string;

    constructor(form: HtmlForm, translator: Translator) {
        super(form, new Map(), translator);
        this.url = form.form.action;
    }

    protected submit(form: HtmlForm): Promise<object> {
        const values = form.fields;
        const download = new Maybe<FormField>(values.get('download'));
        const signature = new Maybe<FormField>(values.get('signature'));
        const nightly = new Maybe<FormField>(values.get('nightly'));
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
