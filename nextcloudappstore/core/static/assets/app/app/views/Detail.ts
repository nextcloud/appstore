import {fetchDescription} from '../../api/Api';
import {fetchRatings} from '../../api/Ratings';
import {
    getMetaValue, idOrThrow, query, queryOrThrow, ready,
} from '../../dom/Facades';
import {renderEmptyRatings, renderRating} from '../templates/Ratings';

/* tslint:disable */
declare global {
    interface Window {
        id: any;
        fetchRatings: any;
        fetchDescription: any;
        renderRating: any;
        renderEmptyRatings: any;
        ratingUrl: any;
        descriptUrl: any;
        currentLang: any;
        fallbackLang: any;
        ratingTpl: any;
        noRatingTpl: any;
        ratingContainer: any;
        commentInput: any;
        languageInput: any;
        commentLangInput: any;
        descriptContainer: any;
    }
}

window.fetchRatings = fetchRatings;
window.fetchDescription = fetchDescription;
window.renderRating = renderRating;
window.renderEmptyRatings = renderEmptyRatings;
/* tslint:enable */

ready(() => {
    const ratingUrl = getMetaValue('nextcloudappstore-app-ratings-url')
        .orThrow(() => new Error('App ratings url not found'));

    const descriptUrl = getMetaValue('nextcloudappstore-app-description-url')
        .orThrow(() => new Error('App description url not found'));

    const currentLang = getMetaValue('language-code')
        .orThrow(() => new Error('Current language not found'));

    const fallbackLang = getMetaValue('fallback-language-code')
        .orThrow(() => new Error('Fallback language not found'));

    const ratingTpl = idOrThrow<HTMLTemplateElement>('rating-template');
    const noRatingTpl = idOrThrow<HTMLTemplateElement>('no-ratings-template');
    const commentInput = idOrThrow<HTMLTextAreaElement>('id_comment');
    const languageInput = idOrThrow<HTMLSelectElement>('id_language_code');
    const commentLangInput = idOrThrow<HTMLSelectElement>(
        'comment_display_language_code');
    const actualFallbackLang = query<HTMLOptionElement>(
        `option[value="${fallbackLang}"]`, commentLangInput);

    if (actualFallbackLang) {
        window.fallbackLang = fallbackLang;
    }
    const descriptContainer = queryOrThrow<HTMLDivElement>('.app-description');
    const ratingContainer = queryOrThrow<HTMLDivElement>('.app-rating-list');

    window.ratingUrl = ratingUrl;
    window.descriptUrl = descriptUrl;
    window.currentLang = currentLang;
    window.ratingTpl = ratingTpl;
    window.noRatingTpl = noRatingTpl;
    window.ratingContainer = ratingContainer;
    window.commentInput = commentInput;
    window.languageInput = languageInput;
    window.commentLangInput = commentLangInput;
    window.descriptContainer = descriptContainer;
});
