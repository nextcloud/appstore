import {fetchRatings, findUserComment} from '../../api/Ratings';
import {idOrThrow, queryAll, queryOrThrow, ready} from '../../dom/Facades';
import {renderEmptyRatings, renderRating, renderRatingActions} from '../templates/Ratings';

export interface IRatingTemplateConfig {
    languageChooser: HTMLSelectElement;
    target: HTMLElement;
    templates: {
        empty: HTMLTemplateElement;
        rating: HTMLTemplateElement;
        ratingActions: HTMLTemplateElement,
    };
}

export const ratingConfig: Promise<IRatingTemplateConfig> = ready.then(() => {
    return Promise.resolve({
        languageChooser: idOrThrow('comment_language', HTMLSelectElement),
        target: queryOrThrow('.app-rating-list', HTMLDivElement),
        templates: {
            empty: idOrThrow('no-ratings-template', HTMLTemplateElement),
            rating: idOrThrow('rating-template', HTMLTemplateElement),
            ratingActions: idOrThrow('rating-comment-actions', HTMLTemplateElement),
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
                                config: IRatingTemplateConfig) {
    fetchRatings(url, lang, fallback)
        .then((result) => {
            // update result page
            config.target.classList.remove('loading');
            config.target.innerHTML = '';
            config.languageChooser.value = result.lang;

            result.ratings.forEach((rating) => {
                const tpl = renderRating(config.templates.rating, rating);
                const ratingComment = queryOrThrow('.rating-comment', HTMLElement, tpl);
                config.target.appendChild(tpl);
                const ratingActions = renderRatingActions(config.templates.ratingActions, rating, lang, fallback);
                if (queryAll('.comment-actions-button', ratingActions).length !== 0) {
                    ratingComment.appendChild(ratingActions);
                }
            });

            if (config.target.children.length === 0) {
                const tpl = renderEmptyRatings(config.templates.empty);
                config.target.appendChild(tpl);
            }

            // Scroll to the specific comment if the comment_id is provided in the URL
            const commentId = new URLSearchParams(window.location.search).get('comment_id');
            if (commentId) {
                const element = document.getElementById(`rating-${commentId}`);
                if (element) {
                    element.scrollIntoView();
                }
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
