import {queryAll} from './Facades';
import {TemplateEmpty} from './TemplateEmpty';

/**
 * Escapes a string for including it in HTML
 * @param text
 * @returns {string}
 */
export function escapeHtml(text: string): string {
    const div = window.document.createElement('div');
    div.appendChild(window.document.createTextNode(text));
    return div.innerHTML;
}

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

/**
 * Finds the first root element or throws
 * @param template
 * @throws TemplateEmpty if the root template element is not found
 * @returns {HTMLElement}
 */
function findRoot(template: Node): HTMLElement {
    if (template.childNodes.length === 0) {
        throw new TemplateEmpty('Given template is empty');
    } else {
        return template.childNodes[1] as HTMLElement;
    }
}

export type Context = {
    [selector: string]: string;
};

/**
 * Renders an HTML template
 * @param template the template dom element
 * @param context an object whose keys are selectors and values are ESCAPED
 * values to render to the document
 * @param transformer if given will be executed by passing in the root element
 */
export function render(template: HTMLTemplateElement,
                       context: Context,
                       transformer?: (root: HTMLElement) => void): Node {
    const result = document.importNode(template.content, true);
    const root = findRoot(result);

    Object.keys(context).forEach((selector: string) => {
        queryAll(selector, root).forEach((element: HTMLElement) => {
            element.innerHTML = context[selector];
        });
    });

    if (transformer) {
        transformer(root);
    }

    return result;
}
