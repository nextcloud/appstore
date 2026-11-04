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

ready.then(() => {
    const appIdInput = idOrThrow('app-id', HTMLInputElement);
    const button = idOrThrow('generate-key-cert', HTMLButtonElement);
    const errorMsg = idOrThrow('generate-error', HTMLElement);
    const successMsg = idOrThrow('generate-success', HTMLElement);

    function hideMessages(): void {
        errorMsg.hidden = true;
        successMsg.hidden = true;
        errorMsg.textContent = '';
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

        button.disabled = true;
        button.classList.add('btn-loading');
        try {
            const result = await generateAppCsr(appId);
            downloadPem(`${result.appId}.key`, result.privateKeyPem);
            downloadPem(`${result.appId}.csr`, result.csrPem);
            showSuccess(
                successMsg.getAttribute('data-msg-success') ||
                    'Private key and CSR downloaded. Keep the .key file secret.',
            );
        } catch (e) {
            if (e instanceof InvalidAppIdError) {
                showError(
                    errorMsg.getAttribute('data-msg-invalid') ||
                        'App id must contain only lowercase ASCII letters and underscores.',
                );
            } else {
                showError(
                    errorMsg.getAttribute('data-msg-failed') ||
                        'Could not generate key and CSR. Try again or use openssl.',
                );
            }
        } finally {
            button.disabled = false;
            button.classList.remove('btn-loading');
        }
    });
});
