import {idOrThrow, queryOrThrow, ready} from '../../dom/Facades';
import {fetchRatings, findUserComment} from '../../api/Ratings';
import {renderEmptyRatings, renderRating} from '../templates/Ratings';

export type RatingTemplateConfig = {
    languageChooser: HTMLSelectElement;
    target: HTMLElement;
    templates: {
        empty: HTMLTemplateElement;
        rating: HTMLTemplateElement;
    };
};

export const ratingConfig: Promise<RatingTemplateConfig> = ready().then(() => {
    return Promise.resolve({
        target: queryOrThrow<HTMLDivElement>('.app-rating-list'),
        languageChooser: idOrThrow<HTMLSelectElement>('comment_language'),
        templates: {
            rating: idOrThrow<HTMLTemplateElement>('rating-template'),
            empty: idOrThrow<HTMLTemplateElement>('no-ratings-template'),
        },
    });
});

/**
 * Loads a list of user comments into the specified list section
 * @param url
 * @param lang
 * @param fallback
 * @param config
 */
export function loadUserRatings(url: string, lang: string, fallback: string,
                                config: RatingTemplateConfig) {
    fetchRatings(url, lang, fallback)
        .then((result) => {
            // update result page
            config.target.classList.remove('loading');
            config.target.innerHTML = '';
            config.languageChooser.value = result.lang;

            result.ratings.forEach((rating) => {
                const tpl = renderRating(config.templates.rating, rating,
                    result.lang);
                config.target.appendChild(tpl);
            });

            if (config.target.children.length === 0) {
                const tpl = renderEmptyRatings(config.templates.empty);
                config.target.appendChild(tpl);
            }
        });
}

/**
 * Loads a rating in a language from a user and handles the comment textare
 * @param url
 * @param lang
 * @param input
 */
export function loadUserRating(url: string, lang: string,
                               input: HTMLTextAreaElement) {
    input.readOnly = true;
    fetchRatings(url, lang)
        .then((result) => {
            input.value = findUserComment(result)
                .orElse('');
            input.readOnly = false;
        });
}
