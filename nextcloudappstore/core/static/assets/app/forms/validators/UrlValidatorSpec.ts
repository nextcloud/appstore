/**
 * SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {Invalid} from './Invalid';
import {UrlValidator} from './UrlValidator';
import {Valid} from './Valid';

describe('Testing the URL validator', () => {

    it('should accept http and https URLs', () => {
        const validator = new UrlValidator();
        expect(validator.validate('https://github.com/example/app')
            instanceof Valid).toBe(true);
        expect(validator.validate('http://example.com/repo')
            instanceof Valid).toBe(true);
    });

    it('should reject non-http schemes and garbage', () => {
        const validator = new UrlValidator();
        const ftp = validator.validate('ftp://example.com/repo');
        expect(ftp instanceof Invalid).toBe(true);
        expect((ftp as Invalid).errorMsgId).toBe('msg-invalid-url');

        const garbage = validator.validate('not a url');
        expect(garbage instanceof Invalid).toBe(true);
        expect((garbage as Invalid).errorMsgId).toBe('msg-invalid-url');
    });

});
