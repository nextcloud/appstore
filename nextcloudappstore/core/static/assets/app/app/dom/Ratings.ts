import {fetchRatings, findUserComment} from '../../api/Ratings';
import {idOrThrow, queryOrThrow, ready} from '../../dom/Facades';
import {renderEmptyRatings, renderRating} from '../templates/Ratings';

export interface RatingTemplateConfig {
    languageChooser: HTMLSelectElement;
    target: HTMLElement;
    templates: {
        empty: HTMLTemplateElement;
        rating: HTMLTemplateElement;
    };
}

export const ratingConfig: Promise<RatingTemplateConfig> = ready.then(() => {
    return Promise.resolve({
        languageChooser: idOrThrow<HTMLSelectElement>('comment_language'),
        target: queryOrThrow<HTMLDivElement>('.app-rating-list'),
        templates: {
            empty: idOrThrow<HTMLTemplateElement>('no-ratings-template'),
            rating: idOrThrow<HTMLTemplateElement>('rating-template'),
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
