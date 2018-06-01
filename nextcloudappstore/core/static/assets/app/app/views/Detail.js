import * as screenfull from 'screenfull';
import { fetchDescription } from '../../api/Api';
import { getMetaValueOrThrow, id, idOrThrow, queryOrThrow, ready, } from '../../dom/Facades';
import { loadUserRating, loadUserRatings, ratingConfig } from '../dom/Ratings';
ready.then(() => {
    const ratingUrl = getMetaValueOrThrow('ratings-url');
    const descriptionUrl = getMetaValueOrThrow('description-url');
    const currentLang = getMetaValueOrThrow('language-code');
    const fallbackLang = getMetaValueOrThrow('fallback-language-code');
    id('id_comment', HTMLTextAreaElement)
        .ifPresent((commentInput) => {
        const input = idOrThrow('id_language_code', HTMLSelectElement);
        input.addEventListener('change', (event) => {
            const target = event.target;
            const lang = target.value;
            const url = `${ratingUrl}?current_user=true&lang=${lang}`;
            loadUserRating(url, lang, commentInput);
        });
    });
    const descriptionTarget = queryOrThrow('.app-description', HTMLElement);
    fetchDescription(descriptionUrl)
        .then((description) => {
        descriptionTarget.innerHTML = description;
        descriptionTarget.classList.remove('loading');
    });
    ratingConfig.then((config) => {
        config.languageChooser.addEventListener('change', (event) => {
            const target = event.target;
            loadUserRatings(ratingUrl, target.value, fallbackLang, config);
        });
        loadUserRatings(ratingUrl, currentLang, fallbackLang, config);
    });
    id('app-gallery-container', HTMLElement).ifPresent((gallery) => {
        const item = queryOrThrow('.carousel-inner', HTMLElement, gallery);
        item.addEventListener('click', () => {
            if (screenfull.enabled) {
                item.classList.toggle('fullscreen');
                screenfull.toggle(gallery);
            }
        });
    });
});
//# sourceMappingURL=Detail.js.map