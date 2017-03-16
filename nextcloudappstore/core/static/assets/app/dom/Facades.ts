/**
 * shortcuts for unreasonably long DOM methods
 */

export function id(selector: string): HTMLElement | null {
    return window.document.getElementById(selector);
}

export function query(selector: string): Element | null {
    return window.document.querySelector(selector);
}

export function queryAll(selector: string): Array<Element> {
    return Array.from(window.document.querySelectorAll(selector));
}

export function getMetaValue(name: string): string | null {
    const result = query(`meta[name="${name}]"`);
    if (result === undefined) {
        return null;
    } else {
        const metaTag = result as HTMLMetaElement;
        return metaTag.content;
    }
}
