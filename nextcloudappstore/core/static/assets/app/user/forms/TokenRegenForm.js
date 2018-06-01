import { apiRequest, HttpMethod } from '../../api/Request';
import { AjaxForm } from '../../forms/AjaxForm';
export class TokenRegenForm extends AjaxForm {
    constructor(form, translator, tokenElement) {
        super(form, new Map(), translator);
        this.tokenElement = tokenElement;
        this.url = form.form.action;
    }
    submit(_) {
        const data = {
            data: {},
            method: HttpMethod.POST,
            url: this.url,
        };
        return apiRequest(data, this.findCsrfToken())
            .then((response) => {
            this.tokenElement.innerText = response.token;
            return Promise.resolve.bind(Promise);
        });
    }
}
//# sourceMappingURL=TokenRegenForm.js.map