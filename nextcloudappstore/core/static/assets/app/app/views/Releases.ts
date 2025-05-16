/**
 * SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {createAccordion} from '../../components/Accordion';
import {queryAll, ready} from '../../dom/Facades';

ready.then(() => {
    queryAll('.accordion-item').forEach(createAccordion);
});
