import { Maybe } from '../Utils';
import { DomElementDoesNotExist } from './DomElementDoesNotExist';
export function id(selector, type) {
    return new Maybe(document.getElementById(selector))
        .filter((elem) => elem instanceof type);
}
export function query(selector, type, parent) {
    const elem = parent || window.document;
    return new Maybe(elem.querySelector(selector))
        .filter((result) => result instanceof type);
}
export function queryAll(selector, parent) {
    const elem = parent || window.document;
    return Array.from(elem.querySelectorAll(selector));
}
export function idOrThrow(selector, type) {
    return id(selector, type)
        .orThrow(() => {
        const msg = `No element found for id ${selector}`;
        throw new DomElementDoesNotExist(msg);
    });
}
export function queryOrThrow(selector, type, parent) {
    return query(selector, type, parent)
        .orThrow(() => {
        const msg = `No element found for selector ${selector}`;
        throw new DomElementDoesNotExist(msg);
    });
}
export function getMetaValue(name) {
    return query(`meta[name="${name}"]`, HTMLMetaElement)
        .map((elem) => elem.content);
}
export function getMetaValueOrThrow(name) {
    const msg = `Meta tag with name ${name} not found`;
    return getMetaValue(name)
        .orThrow(() => new DomElementDoesNotExist(msg));
}
export function removeElements(selector) {
    queryAll(selector)
        .forEach((elem) => elem.remove());
}
export function toHtml(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return new Maybe(tmp.querySelector('*'));
}
export function appendHtml(parentSelector, type, html) {
    const parent = queryOrThrow(parentSelector, type);
    const child = toHtml(html)
        .orThrow(() => new DomElementDoesNotExist('Child does not exist'));
    parent.appendChild(child);
    return child;
}
export function testDom(parentSelector, type, html, callback) {
    const elem = appendHtml(parentSelector, type, html);
    callback(elem);
    elem.remove();
}
export const ready = new Promise((resolve) => {
    document.addEventListener('DOMContentLoaded', resolve);
});
//# sourceMappingURL=Facades.js.map