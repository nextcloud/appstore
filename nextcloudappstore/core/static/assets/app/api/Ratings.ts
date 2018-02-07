import {Maybe} from '../Utils';
import {pageRequest} from './Request';

export interface IRatings {
    lang: string;
    ratings: IRating[];
}

export interface IRating {
    comment: string;
    fullUserName: string;
    ratedAt: string;
    relativeRatedAt: string;
    rating: {
        name: string;
        value: number;
    };
}

interface IApiRating {
    ratedAt: string;
    relativeRatedAt: string;
    rating: number;
    translations: {
        [index: string]: {
            comment: string;
        } | undefined,
    };
    user: {
        firstName: string;
        lastName: string;
    };
}

export function filterEmptyComments(ratings: IApiRating[],
                                    lang: string): IApiRating[] {
    return ratings.filter((rating) => {
        const translations = rating.translations;
        const languages = translations[lang];
        return languages !== undefined &&
            languages.comment !== undefined &&
            languages.comment.trim() !== '';
    });
}

/**
 * Turns a float into a descriptive name
 * @param value
 * @returns {any}
 */
export function createRatingName(value: number): string {
    // because floats
    if (value >= .999999999) {
        return 'good';
    } else if (value <= 0.000000001) {
        return 'bad';
    } else {
        return 'ok';
    }
}

/**
 * Converts the rating from the API into a simpler data structure
 * @param rating
 * @param lang
 * @returns
 */
export function convertRating(rating: IApiRating, lang: string): IRating {
    let fullName = `${rating.user.firstName} ${rating.user.lastName}`;
    if (fullName.trim() === '') {
        fullName = 'Anonymous';
    }
    const translation = rating.translations[lang] || {comment: ''};
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

/**
 * Fetches a list of ratings for a language
 * @param url where the comments are located
 * @param lang language to load
 * @param fallbackLang language code to fall back if no comments are found
 * @returns a promise with ratings and the actual used language
 */
export function fetchRatings(url: string, lang: string,
                             fallbackLang?: string): Promise<IRatings> {
    return pageRequest({url, data: {}})
        .then((apiRatings: IApiRating[]) => {
            const ratings = filterEmptyComments(apiRatings, lang)
                .map((rating: IApiRating) => convertRating(rating, lang));

            if (ratings.length > 0 || !fallbackLang) {
                return Promise.resolve({lang, ratings});
            } else {
                return fetchRatings(url, fallbackLang);
            }
        });
}

/**
 * Fetches the first rating comment from a rating result
 * @param result
 * @returns
 */
export function findUserComment(result: IRatings): Maybe<string> {
    return new Maybe(result.ratings)
        .map((ratings) => ratings[0])
        .map((rating: IRating) => rating.comment);
}
