import {fetchToken} from '../../api/Request';
import {queryOrThrow, ready} from '../../dom/Facades';
import {scanForm} from '../../forms/HtmlForm';
import {scanTranslations, Translator} from '../../l10n/Translator';
import {Maybe} from '../../Utils';
import {TokenRegenForm} from '../forms/TokenRegenForm';

ready.then(() => {
    const formElement = queryOrThrow<HTMLFormElement>('#api-token-regen-form');
    const formMeta = scanForm(formElement);
    const translations = scanTranslations(formElement);
    const translator = new Translator(translations);
    const tokenElement = queryOrThrow<HTMLElement>('#token');
    const form = new TokenRegenForm(formMeta, translator, tokenElement);

    // needs to be done in JS to prevent BREACH attack
    new Maybe(formMeta.fields.get('csrfmiddlewaretoken'))
        .map((elem) => elem.value)
        .ifPresent((csrfToken) => {
            fetchToken(csrfToken)
                .then((token) => tokenElement.innerText = token);
        });
});
