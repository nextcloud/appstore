/**
 * SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {CsrValidator} from './CsrValidator';
import {Invalid} from './Invalid';
import {Valid} from './Valid';

describe('Testing the certificate signing request', () => {

    it('should accept a correct CSR', () => {
        const validator = new CsrValidator();
        const input = '-----BEGIN CERTIFICATE REQUEST-----\n' +
            '-----END CERTIFICATE REQUEST-----';

        const result = validator.validate(input);
        expect(result instanceof Valid).toBe(true);
    });

    it('should fail for an incorrect CSR', () => {
        const validator = new CsrValidator();
        const input = '-----BEGIN CERTIFICATE-----\n' +
            '-----END CERTIFICATE-----';

        const result = validator.validate(input);
        expect(result instanceof Invalid).toBe(true);
        expect((result as Invalid).errorMsgId).toBe('msg-invalid-csr');
    });

});
