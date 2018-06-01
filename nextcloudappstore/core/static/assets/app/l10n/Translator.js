import { queryAll } from '../dom/Facades';
import { NoTranslationFound } from './NoTranslationFound';
export class Translator {
    constructor(translations) {
        this.translations = translations;
    }
    get(id) {
        const result = this.translations.get(id);
        if (result === undefined) {
            const msg = `Could not find translation for id ${id}`;
            throw new NoTranslationFound(msg);
        }
        else {
            return result;
        }
    }
}
export function scanTranslations(root) {
    const result = new Map();
    const translations = queryAll('[data-l10n-id]', root);
    const dataKey = 'l10nId';
    translations.forEach((elem) => {
        const id = elem.dataset[dataKey];
        const value = elem.textContent;
        if (id === undefined) {
            const msg = `Found improperly configured translation for ${elem}`;
            console.error(msg);
        }
        else {
            result.set(id, value || '');
        }
    });
    return result;
}
//# sourceMappingURL=Translator.js.map