/**
 * SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {AppIdValidator} from './AppIdValidator';
import {Invalid} from './Invalid';
import {Valid} from './Valid';

describe('AppIdValidator', () => {
    const validator = new AppIdValidator();

    it('accepts valid app IDs', () => {
        expect(validator.validate('news') instanceof Valid).toBe(true);
        expect(validator.validate('twofactor_gateway') instanceof Valid).toBe(true);
    });

    it('rejects invalid characters', () => {
        const result = validator.validate('News');
        expect(result instanceof Invalid).toBe(true);
        expect((result as Invalid).errorMsgId).toBe('msg-invalid-app-id');
    });

    it('rejects IDs longer than 32 characters', () => {
        const result = validator.validate('a'.repeat(33));
        expect(result instanceof Invalid).toBe(true);
        expect((result as Invalid).errorMsgId).toBe('msg-app-id-too-long');
    });
});
