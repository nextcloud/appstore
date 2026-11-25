/**
 * SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {Invalid} from './Invalid';
import {IValidator} from './IValidator';
import {Valid} from './Valid';

export class UrlValidator implements IValidator {

    public validate(value: string): Valid | Invalid {
        try {
            const url = new URL(value);
            if (url.protocol === 'http:' || url.protocol === 'https:') {
                return new Valid();
            }
        } catch {
            // not a valid absolute URL
        }
        return new Invalid('msg-invalid-url');
    }

}
