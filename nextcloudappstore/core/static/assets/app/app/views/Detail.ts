import {fetchDescription} from '../../api/Api';
import {fetchRatings} from '../../api/Ratings';
import {
    getMetaValueOrThrow, idOrThrow, query, queryOrThrow, ready,
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
    const ratingUrl = getMetaValueOrThrow('ratings-url');
    const descriptUrl = getMetaValueOrThrow('description-url');
    const currentLang = getMetaValueOrThrow('language-code');
    const fallbackLang = getMetaValueOrThrow('fallback-language-code');

    const ratingTpl = idOrThrow<HTMLTemplateElement>('rating-template');
    const noRatingTpl = idOrThrow<HTMLTemplateElement>('no-ratings-template');
    const commentInput = idOrThrow<HTMLTextAreaElement>('id_comment');
    const languageInput = idOrThrow<HTMLSelectElement>('id_language_code');
    const commentLangInput = idOrThrow<HTMLSelectElement>('comment_language');

    const descriptContainer = queryOrThrow<HTMLDivElement>('.app-description');
    const ratingContainer = queryOrThrow<HTMLDivElement>('.app-rating-list');

    window.ratingUrl = ratingUrl;
    window.descriptUrl = descriptUrl;
    window.currentLang = currentLang;
    window.fallbackLang = fallbackLang;
    window.ratingTpl = ratingTpl;
    window.noRatingTpl = noRatingTpl;
    window.ratingContainer = ratingContainer;
    window.commentInput = commentInput;
    window.languageInput = languageInput;
    window.commentLangInput = commentLangInput;
    window.descriptContainer = descriptContainer;
});
