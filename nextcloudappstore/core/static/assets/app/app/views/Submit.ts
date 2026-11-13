/**
 * SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {downloadPem} from '../../crypto/downloadPem';
import {
    generateAppCsr,
    InvalidAppIdError,
} from '../../crypto/generateAppCsr';
import {idOrThrow, ready} from '../../dom/Facades';
import {scanForm} from '../../forms/HtmlForm';
import {CsrValidator} from '../../forms/validators/CsrValidator';
import {IValidator} from '../../forms/validators/IValidator';
import {UrlValidator} from '../../forms/validators/UrlValidator';
import {scanTranslations, Translator} from '../../l10n/Translator';
import {AppSubmitForm} from '../forms/AppSubmitForm';

ready.then(() => {
    const formElement = idOrThrow('app-submit-form', HTMLFormElement);
    const formMeta = scanForm(formElement);
    const validators = new Map<string, IValidator[]>();
    validators.set('repository', [new UrlValidator()]);
    validators.set('csr', [new CsrValidator()]);
    const translations = scanTranslations(formElement);
    const translator = new Translator(translations);
    const form = new AppSubmitForm(formMeta, validators, translator);
    form.bindListeners();

    const appIdInput = idOrThrow('id_app_id', HTMLInputElement);
    const csrInput = idOrThrow('id_csr', HTMLTextAreaElement);
    const button = idOrThrow('generate-key-cert', HTMLButtonElement);
    const errorMsg = idOrThrow('generate-error', HTMLElement);
    const successMsg = idOrThrow('generate-success', HTMLElement);

    function hideMessages(): void {
        errorMsg.hidden = true;
        successMsg.hidden = true;
        errorMsg.textContent = '';
        successMsg.textContent = '';
    }

    function showError(message: string): void {
        successMsg.hidden = true;
        errorMsg.textContent = message;
        errorMsg.hidden = false;
    }

    function showSuccess(message: string): void {
        errorMsg.hidden = true;
        successMsg.textContent = message;
        successMsg.hidden = false;
    }

    button.addEventListener('click', async () => {
        hideMessages();
        const appId = appIdInput.value.trim();
        if (!appId) {
            showError(translator.get('msg-empty-app-id'));
            return;
        }

        button.disabled = true;
        button.classList.add('btn-loading');
        try {
            const result = await generateAppCsr(appId);
            downloadPem(`${appId}.key`, result.privateKeyPem);
            csrInput.value = result.csrPem;
            csrInput.dispatchEvent(new Event('change', {bubbles: true}));
            showSuccess(translator.get('msg-generate-success'));
        } catch (e) {
            if (e instanceof InvalidAppIdError) {
                showError(translator.get('msg-invalid-app-id'));
            } else {
                showError(translator.get('msg-generate-failed'));
            }
        } finally {
            button.disabled = false;
            button.classList.remove('btn-loading');
        }
    });
});
