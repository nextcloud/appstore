/**
 * SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {Invalid} from './Invalid';
import {Valid} from './Valid';

export interface IValidator {
    validate(value: string): Valid | Invalid;
}
