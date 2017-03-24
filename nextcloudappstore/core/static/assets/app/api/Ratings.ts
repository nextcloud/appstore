import {Maybe} from '../Utils';
import {pageRequest} from './Request';

export type Ratings = {
    lang: string;
    ratings: Rating[];
};

export type Rating = {
    comment: string;
    fullUserName: string;
    ratedAt: string;
    rating: {
        name: string;
        value: number;
    };
};

type ApiRating = {
    ratedAt: string;
    rating: number;
    translations: {
        [index: string]: {
            comment: string;
        },
    };
    user: {
        firstName: string;
        lastName: string;
    };
};

export function filterEmptyComments(ratings: ApiRating[],
                                    lang: string): ApiRating[] {
    return ratings.filter((rating) => {
        const translations = rating.translations;
        return translations[lang] !== undefined &&
            translations[lang].comment !== undefined &&
            translations[lang].comment.trim() !== '';
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
export function convertRating(rating: ApiRating, lang: string): Rating {
    let fullName = `${rating.user.firstName} ${rating.user.lastName}`;
    if (fullName.trim() === '') {
        fullName = 'Anonymous';
    }
    return {
        comment: rating.translations[lang].comment,
        fullUserName: fullName.trim(),
        ratedAt: rating.ratedAt,
        rating: {
            name: createRatingName(rating.rating),
            value: rating.rating,
        },
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
                             fallbackLang?: string): Promise<Ratings> {
    return pageRequest({url, data: {}})
        .then((apiRatings: ApiRating[]) => {
            const ratings = filterEmptyComments(apiRatings, lang)
                .map((rating: ApiRating) => convertRating(rating, lang));

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
export function findUserComment(result: Ratings): Maybe<string> {
    return new Maybe(result.ratings)
        .map((ratings) => ratings[0])
        .map((rating: Rating) => rating.comment);
}
