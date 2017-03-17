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
        .forEach(link => link.rel = 'noopener noreferrer');
    return doc.body.innerHTML;
}
