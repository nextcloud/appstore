import * as hljs from 'highlight.js';
import * as markdownit from 'markdown-it';
import { noReferrerLinks } from './Templating';
export function renderMd(html) {
    const md = markdownit({
        highlight: (str, lang) => {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(lang, str).value;
                }
                catch (e) {
                    console.error(e);
                }
            }
            return '';
        },
    });
    return noReferrerLinks(md.render(html));
}
//# sourceMappingURL=Markdown.js.map