/**
 * shortcuts for unreasonably long DOM methods
 */

import {DomElementDoesNotExist} from './DomElementDoesNotExist';

export function id(selector: string): HTMLElement | null {
    return window.document.getElementById(selector);
}

export function query<T extends Element>(selector: string,
                                         parent?: Element): T | null {
    const elem = parent || window.document;
    return elem.querySelector(selector) as T;
}

export function queryAll(selector: string, parent?: Element): Element[] {
    const elem = parent || window.document;
    return Array.from(elem.querySelectorAll(selector));
}

/**
 * Similar to query but throws if no element is found
 * use this function to fail early if you absolutely expect it to not return
 * null
 * @param selector selector to use
 * @param parent element to start the search from if given, otherwise document
 * @throws DomElementDoesNotExist if the query returns no element
 */
export function queryOrThrow<T extends HTMLElement>(selector: string,
                                                    parent?: Element): T {
    const elem = query<T>(selector, parent);
    if (elem === null) {
        const msg = `No element found for selector ${selector}`;
        throw new DomElementDoesNotExist(msg);
    } else {
        return elem;
    }
}

/**
 * Parses the header for a meta tag with a certain name and returns the content
 * @param name
 * @returns {any}
 */
export function getMetaValue(name: string): string | null {
    const result = query(`meta[name="${name}"]`);
    if (result === null || !(result instanceof HTMLMetaElement)) {
        return null;
    } else {
        const metaTag = result as HTMLMetaElement;
        return metaTag.content;
    }
}

/**
 * Remove elements from the dom
 * @param selector selector that matches the elements
 */
export function removeElements(selector: string): void {
    queryAll(selector)
        .forEach((elem) => elem.remove());
}

/**
 * Turns a string into html if possible
 * @param html must have a root element
 * @returns {Element}
 */
export function toHtml<T extends Element>(html: string): T | null {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.querySelector('*') as T;
}

/**
 * Appends an HTML string to a parent element
 * @param parentSelector selector to find the parent
 * @param html Html string, must have a root element
 * @throws Error if either parent or Html is invalid
 * @returns {Element}
 */
export function appendHtml(parentSelector: string, html: string): Element {
    const parent = query(parentSelector);
    const child = toHtml(html);

    if (parent === null || child === null) {
        throw new Error('Parent or child are null');
    } else {
        parent.appendChild(child);
    }

    return child;
}

/**
 * Inserts html into the dom, executes a function and then removes the inserted
 * element again
 * @param parentSelector selector where to insert the html
 * @param html actual html
 * @param callback function that is executed in between
 */
export function testDom(parentSelector: string, html: string,
                        callback: (elem: Element) => void): void {
    const elem = appendHtml(parentSelector, html);
    callback(elem);
    elem.remove();
}

/**
 * Similar to $.ready
 * @param callback to execute after the dom has loaded
 */
export function ready(callback: () => void) {
    if (document.readyState !== 'loading') {
        callback();
    } else {
        document.addEventListener('DOMContentLoaded', callback);
    }
}
