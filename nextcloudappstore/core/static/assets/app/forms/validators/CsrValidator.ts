/**
 * SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {Invalid} from './Invalid';
import {IValidator} from './IValidator';
import {Valid} from './Valid';

export class CsrValidator implements IValidator {

    public validate(csr: string): Valid | Invalid {
        if (csr.startsWith('-----BEGIN CERTIFICATE REQUEST-----') &&
            csr.endsWith('-----END CERTIFICATE REQUEST-----')) {
            return new Valid();
        } else {
            return new Invalid('msg-invalid-csr');
        }
    }

}
