import {queryAll} from '../dom/Facades';
import {NoTranslationFound} from './NoTranslationFound';

export class Translator {

    constructor(private readonly translations: Map<string, string>) {
    }

    public get(id: string): string {
        const result = this.translations.get(id);
        if (result === undefined) {
            const msg = `Could not find translation for id ${id}`;
            throw new NoTranslationFound(msg);
        } else {
            return result;
        }
    }
}

/**
 * Based on a root element finds all children elements that have data-l10n-id
 * attributes and extracts their text as translation
 * @param root
 * @returns {Map<string, string>}
 */
export function scanTranslations(root: HTMLElement): Map<string, string> {
    const result = new Map<string, string>();
    const translations = queryAll('[data-l10n-id]', root);
    const dataKey = 'l10nId';
    translations.forEach((elem: HTMLElement) => {
        const id = elem.dataset[dataKey];
        const value = elem.textContent;
        if (id === undefined) {
            const msg = `Found improperly configured translation for ${elem}`;
            console.error(msg);
        } else {
            result.set(id, value || '');
        }
    });
    return result;
}
