import {apiRequest, HttpMethod, ITokenData} from '../../api/Request';
import {AjaxForm} from '../../forms/AjaxForm';
import {HtmlForm} from '../../forms/HtmlForm';
import {Translator} from '../../l10n/Translator';

export class TokenRegenForm extends AjaxForm<object> {
    private readonly url: string;

    constructor(form: HtmlForm, translator: Translator,
                private readonly tokenElement: HTMLElement) {
        super(form, new Map(), translator);
        this.url = form.form.action;
    }

    protected submit(_: HtmlForm): Promise<object> {
        const data = {
            data: {},
            method: HttpMethod.POST,
            url: this.url,
        };
        return apiRequest(data, this.findCsrfToken())
            .then((response: ITokenData) => {
                this.tokenElement.innerText = response.token;
                return Promise.resolve.bind(Promise);
            });
    }

}
