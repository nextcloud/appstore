/**
 * SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import hljs from 'highlight.js';
import * as MarkdownItNS from 'markdown-it';
import { noReferrerLinks } from './Templating';

type MarkdownItCtor = typeof MarkdownItNS;

function hasDefaultExport(
    mod: typeof MarkdownItNS,
): mod is typeof MarkdownItNS & { default: MarkdownItCtor } {
    return 'default' in mod;
}

const MarkdownIt: MarkdownItCtor = hasDefaultExport(MarkdownItNS) ? MarkdownItNS.default : MarkdownItNS;

export function renderMd(html: string): string {
    const md = new MarkdownIt({
        highlight: (str: string, lang?: string): string => {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(str, { language: lang, ignoreIllegals: false }).value;
                } catch (e) {
                    console.error(e);
                }
            }
            return ''; // use external default escaping
        },
    });
    return noReferrerLinks(md.render(html));
}
