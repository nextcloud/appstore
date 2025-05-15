/**
 * SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {queryOrThrow} from '../dom/Facades';

export function createAccordion(elem: HTMLElement) {
    const title = queryOrThrow('.accordion-title', HTMLElement, elem);
    title.addEventListener('click', () => {
        elem.classList.toggle('open');
    });
}
