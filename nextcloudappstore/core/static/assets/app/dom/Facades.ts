/**
 * shortcuts for unreasonably long DOM methods
 */

import {Maybe} from '../Utils';
import {DomElementDoesNotExist} from './DomElementDoesNotExist';

type Class<T> = new() => T;

/**
 * Typed shortcut for getElementById
 * @param selector the id
 * @param type the expected HTML element type
 * @returns {Maybe<T>}
 */
export function id<T extends HTMLElement>(selector: string,
                                          type: Class<T>): Maybe<T> {
    return new Maybe(document.getElementById(selector) as T)
        .filter((elem) => elem instanceof type);
}

export function query<T extends Element>(selector: string,
                                         type: Class<T>,
                                         parent?: Element): Maybe<T> {
    const elem = parent || window.document;
    return new Maybe(elem.querySelector(selector) as T)
        .filter((result) => result instanceof type);
}

export function queryAll(selector: string, parent?: Element): Element[] {
    const elem = parent || window.document;
    return Array.from(elem.querySelectorAll(selector));
}

/**
 * Similar to id but throws if no element is found
 * use this function to fail early if you absolutely expect it to not return
 * null
 * @param selector id to use
 * @param type the expected HTML element type
 * @throws DomElementDoesNotExist if the query returns no element
 */
export function idOrThrow<T extends HTMLElement>(selector: string,
                                                 type: Class<T>): T {
    return id<T>(selector, type)
        .orThrow(() => {
            const msg = `No element found for id ${selector}`;
            throw new DomElementDoesNotExist(msg);
        });
}

/**
 * Similar to query but throws if no element is found
 * use this function to fail early if you absolutely expect it to not return
 * null
 * @param selector selector to use
 * @param type the expected HTML element type
 * @param parent element to start the search from if given, otherwise document
 * @throws DomElementDoesNotExist if the query returns no element
 */
export function queryOrThrow<T extends Element>(selector: string,
                                                type: Class<T>,
                                                parent?: Element): T {
    return query<T>(selector, type, parent)
        .orThrow(() => {
            const msg = `No element found for selector ${selector}`;
            throw new DomElementDoesNotExist(msg);
        });
}

/**
 * Parses the header for a meta tag with a certain name and returns the content
 * @param name
 * @returns {any}
 */
export function getMetaValue(name: string): Maybe<string> {
    return query(`meta[name="${name}"]`, HTMLMetaElement)
        .map((elem) => (elem as HTMLMetaElement).content);
}

/**
 * Parses the header for a meta tag with a certain name and returns the content
 * @param name
 * @throws DomElementDoesNotExist if not found
 * @returns {any}
 */
export function getMetaValueOrThrow(name: string): string {
    const msg = `Meta tag with name ${name} not found`;
    return getMetaValue(name)
        .orThrow(() => new DomElementDoesNotExist(msg));
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
export function toHtml<T extends Element>(html: string): Maybe<T> {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return new Maybe(tmp.querySelector('*') as T);
}

/**
 * Appends an HTML string to a parent element
 * @param parentSelector selector to find the parent
 * @param type the expected HTML element type
 * @param html Html string, must have a root element
 * @throws DomElementDoesNotExist if either parent or Html is invalid
 * @returns {Element}
 */
export function appendHtml<T extends HTMLElement>(parentSelector: string,
                                                  type: Class<T>,
                                                  html: string): Element {
    const parent = queryOrThrow(parentSelector, type);
    const child = toHtml(html)
        .orThrow(() => new DomElementDoesNotExist('Child does not exist'));
    parent.appendChild(child);
    return child;
}

/**
 * Inserts html into the dom, executes a function and then removes the inserted
 * element again
 * @param parentSelector selector where to insert the html
 * @param type the expected HTML element type
 * @param html actual html
 * @param callback function that is executed in between
 */
type ElemCallback = (elem: Element) => void;

export function testDom<T extends HTMLElement>(parentSelector: string,
                                               type: Class<T>,
                                               html: string,
                                               callback: ElemCallback): void {
    const elem = appendHtml(parentSelector, type, html);
    callback(elem);
    elem.remove();
}

/**
 * Similar to $.ready however uses a promise
 * @return a promise that resolves once the document has loaded
 */
export const ready = new Promise((resolve) => {
    document.addEventListener('DOMContentLoaded', resolve);
});
