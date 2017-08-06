import {fetchToken} from '../../api/Request';
import {queryOrThrow, ready} from '../../dom/Facades';
import {scanForm} from '../../forms/HtmlForm';
import {scanTranslations, Translator} from '../../l10n/Translator';
import {Maybe} from '../../Utils';
import {TokenRegenForm} from '../forms/TokenRegenForm';

ready.then(() => {
    const formElement = queryOrThrow('#api-token-regen-form', HTMLFormElement);
    const formMeta = scanForm(formElement);
    const translations = scanTranslations(formElement);
    const translator = new Translator(translations);
    const tokenElement = queryOrThrow('#token', HTMLElement);
    const form = new TokenRegenForm(formMeta, translator, tokenElement);
    const button = queryOrThrow('#api-token-regen-form ' +
        'input[type="submit"]', HTMLInputElement);
    form.bindListeners();

    // needs to be done in JS to prevent BREACH attack
    new Maybe(formMeta.fields.get('csrfmiddlewaretoken'))
        .map((elem) => elem.value)
        .ifPresent((csrfToken) => {
            fetchToken(csrfToken)
                .then((token) => {
                    tokenElement.innerText = token;
                    button.disabled = false;
                });
        });
});
