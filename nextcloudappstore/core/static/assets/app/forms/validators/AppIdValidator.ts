/**
 * SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {APP_ID_MAX_LENGTH, isValidAppId} from '../../crypto/generateAppCsr';
import {Invalid} from './Invalid';
import {IValidator} from './IValidator';
import {Valid} from './Valid';

export class AppIdValidator implements IValidator {

    public validate(value: string): Valid | Invalid {
        if (!isValidAppId(value)) {
            if (value.length > APP_ID_MAX_LENGTH) {
                return new Invalid('msg-app-id-too-long');
            }
            return new Invalid('msg-invalid-app-id');
        }
        return new Valid();
    }

}
