/**
 * SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {apiRequest, HttpMethod} from '../../api/Request';
import {AjaxForm} from '../../forms/AjaxForm';
import {FormField, HtmlForm} from '../../forms/HtmlForm';
import {IValidator} from '../../forms/validators/IValidator';
import {Translator} from '../../l10n/Translator';
import {Maybe} from '../../Utils';

export interface AppSubmitResponse {
    pullRequestUrl: string;
}

export class AppSubmitForm extends AjaxForm<AppSubmitResponse> {
    private readonly url: string;

    constructor(form: HtmlForm,
                validators: Map<string, IValidator[]>,
                translator: Translator) {
        super(form, validators, translator);
        this.url = form.form.action;
    }

    protected submit(form: HtmlForm): Promise<AppSubmitResponse> {
        const values = form.fields;
        const appId = new Maybe<FormField>(values.get('app_id'));
        const repository = new Maybe<FormField>(values.get('repository'));
        const csr = new Maybe<FormField>(values.get('csr'));
        const data = {
            data: {
                app_id: appId.map((field) => field.value.trim()).orElse(''),
                csr: csr.map((field) => field.value.trim()).orElse(''),
                repository: repository
                    .map((field) => field.value.trim())
                    .orElse(''),
            },
            method: HttpMethod.POST,
            url: this.url,
        };
        return apiRequest(data, this.findCsrfToken());
    }

    protected onSuccess(result: AppSubmitResponse): void {
        const message = this.translator.get('msg-form-success');
        const linkText = this.translator.get('msg-pr-link');
        const el = this.form.globalSuccessMessage;
        if (el.parentElement !== null) {
            el.textContent = '';
            el.appendChild(document.createTextNode(`${message} `));
            const link = document.createElement('a');
            link.href = result.pullRequestUrl;
            link.textContent = linkText;
            link.rel = 'noopener noreferrer';
            link.target = '_blank';
            el.appendChild(link);
            el.hidden = false;
        }
        this.form.form.reset();
    }
}
