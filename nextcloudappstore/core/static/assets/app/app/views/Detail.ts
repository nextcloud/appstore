import * as screenfull from 'screenfull';
import {fetchDescription} from '../../api/Api';
import {
    getMetaValueOrThrow, id, idOrThrow, queryOrThrow, ready,
} from '../../dom/Facades';
import {loadUserRating, loadUserRatings, ratingConfig} from '../dom/Ratings';

ready.then(() => {
    const ratingUrl = getMetaValueOrThrow('ratings-url');
    const descriptionUrl = getMetaValueOrThrow('description-url');
    const currentLang = getMetaValueOrThrow('language-code');
    const fallbackLang = getMetaValueOrThrow('fallback-language-code');

    // bind rating form language selection if user is logged in
    id('id_comment', HTMLTextAreaElement)
        .ifPresent((commentInput) => {
            const input = idOrThrow('id_language_code', HTMLSelectElement);
            input.addEventListener('change', (event: Event) => {
                const target = event.target as HTMLSelectElement;
                const lang = target.value;
                const url = `${ratingUrl}?current_user=true&lang=${lang}`;
                loadUserRating(url, lang, commentInput);
            });
        });

    // load app description
    const descriptionTarget = queryOrThrow('.app-description', HTMLElement);
    fetchDescription(descriptionUrl)
        .then((description) => {
            descriptionTarget.innerHTML = description;
            descriptionTarget.classList.remove('loading');
        });

    // load user ratings list
    ratingConfig.then((config) => {
        config.languageChooser.addEventListener('change', (event: Event) => {
            const target = event.target as HTMLSelectElement;
            loadUserRatings(ratingUrl, target.value, fallbackLang, config);
        });
        loadUserRatings(ratingUrl, currentLang, fallbackLang, config);
    });

    // fullscreen bindings
    id('app-gallery-container', HTMLElement).ifPresent((gallery) => {
        const item = queryOrThrow('.carousel-inner', HTMLElement, gallery);
        item.addEventListener('click', () => {
            if (screenfull && screenfull.isEnabled) {
                item.classList.toggle('fullscreen');
                screenfull.toggle(gallery);
            }
        });
    });
});
