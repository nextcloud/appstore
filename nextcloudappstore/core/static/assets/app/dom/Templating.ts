import {queryAll} from './Facades';

/**
 * Adds rel="nooopener noreferrer" to all <a> tags in an html string
 * @param html
 * @returns {string}
 */
export function noReferrerLinks(html: string) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    Array.from(doc.getElementsByTagName('a'))
        .forEach((link) => link.rel = 'noopener noreferrer');
    return doc.body.innerHTML;
}

export class Unescaped {
    constructor(public readonly value: string) {}
}

export interface IContext {
    [selector: string]: string | Unescaped;
}

/**
 * Renders an HTML template
 * @param template the template dom element
 * @param context an object whose keys are selectors and values are
 * values to render to the document. Wrap your values in Unescaped if you want
 * to include raw HTML, otherwise everything is escaped
 */
export function render(template: HTMLTemplateElement,
                       context: IContext): HTMLElement {
    const result = document.importNode(template.content, true);

    // result is a WebFragment so we need to make an HTMLElement out of it
    const tmp = document.createElement('div');
    tmp.appendChild(result);
    const root = tmp.children.item(0) as HTMLElement;

    Object.keys(context).forEach((selector: string) => {
        queryAll(selector, root).forEach((element: HTMLElement) => {
            const value = context[selector];
            if (value instanceof Unescaped) {
                element.innerHTML = value.value;
            } else {
                element.innerText = value;
            }
        });
    });

    return root;
}
