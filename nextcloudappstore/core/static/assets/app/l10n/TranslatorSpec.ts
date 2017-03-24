import {DomElementDoesNotExist} from '../dom/DomElementDoesNotExist';
import {toHtml} from '../dom/Facades';
import {NoTranslationFound} from './NoTranslationFound';
import {scanTranslations, Translator} from './Translator';

const translations = `
<div>
    <p data-l10n-id="test">translated</p>
    <p data-l10n-id=""></p>
</div>
`;

describe('Testing l10n translation', () => {

    it('should parse translations', () => {
        const root = toHtml<HTMLDivElement>(translations)
            .orThrow(() => new DomElementDoesNotExist('No element found'));
        const scannedTranslations = scanTranslations(root);
        const translator = new Translator(scannedTranslations);
        expect(translator.get('test')).toBe('translated');

        const msg = 'Could not find translation for id test2';
        expect(() => translator.get('test2'))
            .toThrow(new NoTranslationFound(msg));
    });

});
