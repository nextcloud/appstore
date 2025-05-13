/**
 * SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {renderMd} from '../dom/Markdown';

export function fetchDescription(url: string): Promise<string> {
    return fetch(url)
        .then((response) => response.text())
        .then((description) => Promise.resolve(renderMd(description)));
}
