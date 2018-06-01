import { renderMd } from '../dom/Markdown';
export function fetchDescription(url) {
    return fetch(url)
        .then((response) => response.text())
        .then((description) => Promise.resolve(renderMd(description)));
}
//# sourceMappingURL=Api.js.map