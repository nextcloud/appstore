import {apiRequest, HttpMethod, TokenData} from '../../api/Request';
import {AjaxForm} from '../../forms/AjaxForm';
import {FormField, HtmlForm} from '../../forms/HtmlForm';
import {Translator} from '../../l10n/Translator';

export class TokenRegenForm extends AjaxForm<Object> {
    private url: string;

    constructor(form: HtmlForm, translator: Translator,
                private tokenElement: HTMLElement) {
        super(form, new Map(), translator);
        this.url = form.form.action;
    }

    protected submit(values: Map<string, FormField>): Promise<Object> {
        const data = {
            data: {},
            method: HttpMethod.POST,
            url: this.url,
        };
        return apiRequest(data, this.findCsrfToken())
            .then((response: TokenData) => {
                this.tokenElement.innerText = response.token;
                return Promise.resolve.bind(Promise);
            });
    }

}
