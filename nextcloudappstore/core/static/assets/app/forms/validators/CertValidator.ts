/**
 * SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {Invalid} from './Invalid';
import {IValidator} from './IValidator';
import {Valid} from './Valid';

export class CertValidator implements IValidator {

    public validate(certificate: string): Valid | Invalid {
        if (certificate.startsWith('-----BEGIN CERTIFICATE-----') &&
            certificate.endsWith('-----END CERTIFICATE-----')) {
            return new Valid();
        } else {
            return new Invalid('msg-invalid-certificate');
        }
    }

}
