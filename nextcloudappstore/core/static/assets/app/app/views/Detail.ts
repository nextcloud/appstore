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
    id<HTMLTextAreaElement>('id_comment')
        .ifPresent((commentInput) => {
            const input = idOrThrow<HTMLSelectElement>('id_language_code');
            input.addEventListener('change', (event: Event) => {
                const target = <HTMLSelectElement> event.target;
                const lang = target.value;
                const url = `${ratingUrl}?current_user=true&lang=${lang}`;
                loadUserRating(url, lang, commentInput);
            });
        });

    // load app description
    const descriptionTarget = queryOrThrow<HTMLDivElement>('.app-description');
    fetchDescription(descriptionUrl)
        .then((description) => {
            descriptionTarget.innerHTML = description;
            descriptionTarget.classList.remove('loading');
        });

    // load user ratings list
    ratingConfig.then((config) => {
        config.languageChooser.addEventListener('change', (event: Event) => {
            const target = <HTMLSelectElement> event.target;
            loadUserRatings(ratingUrl, target.value, fallbackLang, config);
        });
        loadUserRatings(ratingUrl, currentLang, fallbackLang, config);
    });

    // fullscreen bindings
    id<HTMLElement>('app-gallery-container').ifPresent((gallery) => {
        const fullscreen = queryOrThrow<HTMLElement>('.fullscreen', gallery);
        fullscreen.addEventListener('click', () => {
            if (screenfull.enabled) {
                screenfull.toggle(gallery);
            }
        });
    });
});
