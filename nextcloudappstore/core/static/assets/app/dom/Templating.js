import { queryAll } from './Facades';
export function noReferrerLinks(html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    Array.from(doc.getElementsByTagName('a'))
        .forEach((link) => link.rel = 'noopener noreferrer');
    return doc.body.innerHTML;
}
export class Unescaped {
    constructor(value) {
        this.value = value;
    }
}
export function render(template, context) {
    const result = document.importNode(template.content, true);
    const tmp = document.createElement('div');
    tmp.appendChild(result);
    const root = tmp.children.item(0);
    Object.keys(context).forEach((selector) => {
        queryAll(selector, root).forEach((element) => {
            const value = context[selector];
            if (value instanceof Unescaped) {
                element.innerHTML = value.value;
            }
            else {
                element.innerText = value;
            }
        });
    });
    return root;
}
//# sourceMappingURL=Templating.js.map