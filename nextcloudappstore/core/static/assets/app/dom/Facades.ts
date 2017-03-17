/**
 * shortcuts for unreasonably long DOM methods
 */

import {DomElementDoesNotExist} from './DomElementDoesNotExist';
import {NotAForm} from './NotAForm';

export function id(selector: string): HTMLElement | null {
    return window.document.getElementById(selector);
}

export function query(selector: string): Element | null {
    return window.document.querySelector(selector);
}

export function queryAll(selector: string): Element[] {
    return Array.from(window.document.querySelectorAll(selector));
}

/**
 * Similar to query but throws if no element is found
 * use this function to fail early if you absolutely expect it to not return
 * null
 * @param selector
 * @throws DomElementDoesNotExist if the query returns no element
 */
export function queryOrThrow(selector: string): Element {
    const elem = query(selector);
    if (elem === null) {
        const msg = `No element found for selector ${selector}`;
        throw new DomElementDoesNotExist(msg);
    } else {
        return elem;
    }
}

/**
 * Finds a form based on a selector
 * @param selector
 * @throws NotAForm if the found element is not a form
 * @throws DomElementDoesNotExist if no element was found
 * @returns {HTMLFormElement}
 */
export function queryForm(selector: string): HTMLFormElement {
    const form = queryOrThrow(selector);
    if (form instanceof HTMLFormElement) {
        return form;
    } else {
        throw new NotAForm(`Element ${form.tagName} is not a form`);
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
export function toHtml(html: string): Element | null {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.querySelector('*');
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
