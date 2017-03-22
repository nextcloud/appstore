import {renderMd} from '../dom/Markdown';

export function fetchDescription(url: string): Promise<string> {
    return fetch(url)
        .then((response) => response.text())
        .then((description) => {
            return Promise.resolve.bind(Promise, renderMd(description));
        });
}
