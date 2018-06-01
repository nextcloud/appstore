import { Maybe } from '../Utils';
import { pageRequest } from './Request';
export function filterEmptyComments(ratings, lang) {
    return ratings.filter((rating) => {
        const translations = rating.translations;
        const languages = translations[lang];
        return languages !== undefined &&
            languages.comment !== undefined &&
            languages.comment.trim() !== '';
    });
}
export function createRatingName(value) {
    if (value >= .999999999) {
        return 'good';
    }
    else if (value <= 0.000000001) {
        return 'bad';
    }
    else {
        return 'ok';
    }
}
export function convertRating(rating, lang) {
    let fullName = `${rating.user.firstName} ${rating.user.lastName}`;
    if (fullName.trim() === '') {
        fullName = 'Anonymous';
    }
    const translation = rating.translations[lang] || { comment: '' };
    return {
        comment: translation.comment,
        fullUserName: fullName.trim(),
        ratedAt: rating.ratedAt,
        rating: {
            name: createRatingName(rating.rating),
            value: rating.rating,
        },
        relativeRatedAt: rating.relativeRatedAt,
    };
}
export function fetchRatings(url, lang, fallbackLang) {
    return pageRequest({ url, data: {} })
        .then((apiRatings) => {
        const ratings = filterEmptyComments(apiRatings, lang)
            .map((rating) => convertRating(rating, lang));
        if (ratings.length > 0 || !fallbackLang) {
            return Promise.resolve({ lang, ratings });
        }
        else {
            return fetchRatings(url, fallbackLang);
        }
    });
}
export function findUserComment(result) {
    return new Maybe(result.ratings)
        .map((ratings) => ratings[0])
        .map((rating) => rating.comment);
}
//# sourceMappingURL=Ratings.js.map