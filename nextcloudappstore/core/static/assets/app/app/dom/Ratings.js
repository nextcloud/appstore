import { fetchRatings, findUserComment } from '../../api/Ratings';
import { idOrThrow, queryOrThrow, ready } from '../../dom/Facades';
import { renderEmptyRatings, renderRating } from '../templates/Ratings';
export const ratingConfig = ready.then(() => {
    return Promise.resolve({
        languageChooser: idOrThrow('comment_language', HTMLSelectElement),
        target: queryOrThrow('.app-rating-list', HTMLDivElement),
        templates: {
            empty: idOrThrow('no-ratings-template', HTMLTemplateElement),
            rating: idOrThrow('rating-template', HTMLTemplateElement),
        },
    });
});
export function loadUserRatings(url, lang, fallback, config) {
    fetchRatings(url, lang, fallback)
        .then((result) => {
        config.target.classList.remove('loading');
        config.target.innerHTML = '';
        config.languageChooser.value = result.lang;
        result.ratings.forEach((rating) => {
            const tpl = renderRating(config.templates.rating, rating);
            config.target.appendChild(tpl);
        });
        if (config.target.children.length === 0) {
            const tpl = renderEmptyRatings(config.templates.empty);
            config.target.appendChild(tpl);
        }
    });
}
export function loadUserRating(url, lang, input) {
    input.readOnly = true;
    fetchRatings(url, lang)
        .then((result) => {
        input.value = findUserComment(result)
            .orElse('');
        input.readOnly = false;
    });
}
//# sourceMappingURL=Ratings.js.map