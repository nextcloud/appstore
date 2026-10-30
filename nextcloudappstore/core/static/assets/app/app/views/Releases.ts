/**
 * SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {id, ready} from '../../dom/Facades';

ready.then(() => {
    id('release-platform', HTMLSelectElement).ifPresent((select) => {
        select.addEventListener('change', () => select.form?.submit());
    });
});
