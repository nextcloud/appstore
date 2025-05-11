/**
 * SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import hljs from 'highlight.js';
import * as markdownit from 'markdown-it';
import {noReferrerLinks} from './Templating';

export function renderMd(html: string): string {
    const md = markdownit({
        highlight: (str, lang) => {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(str, {language: lang, ignoreIllegals: false}).value;
                } catch (e) {
                    console.error(e);
                }
            }
            return ''; // use external default escaping
        },
    });
    return noReferrerLinks(md.render(html));
}
