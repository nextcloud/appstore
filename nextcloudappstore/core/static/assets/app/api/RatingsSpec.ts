import {convertRating, filterEmptyComments} from './Ratings';

describe('Ratings and comments', () => {

    it('filter empty comments', () => {
        const user = {
            firstName: 'tom',
            lastName: 'jones',
        };
        const data = [{
            ratedAt: '2017-03-22T16:54:37.168975Z',
            rating: 0.5,
            relativeRatedAt: '',
            translations: {
                de: {
                    comment: 'blah',
                },
            },
            user,
        }, {
            ratedAt: '2017-03-22T16:54:37.168975Z',
            rating: 0.5,
            relativeRatedAt: '',
            translations: {
                de: {
                    comment: '',
                },
            },
            user,
        }, {
            ratedAt: '2017-03-22T16:54:37.168975Z',
            rating: 0.5,
            relativeRatedAt: '',
            translations: {
                en: {
                    comment: 'blah',
                },
            },
            user,
        }, {
            ratedAt: '2017-03-22T16:54:37.168975Z',
            rating: 0.5,
            relativeRatedAt: '',
            translations: {},
            user,
        }];
        const result = filterEmptyComments(data, 'de');
        expect(result.length).toBe(1);
    });

    it('convert and parse ratings', () => {
        const data = {
            ratedAt: '2017-03-22T16:54:37.168975Z',
            rating: 0.5,
            relativeRatedAt: '',
            translations: {
                de: {
                    comment: 'blah',
                },
            },
            user: {
                firstName: ' Tom',
                lastName: 'Jones',
            },
        };

        const result = convertRating(data, 'de');
        expect(result.comment).toBe('blah');
        expect(result.rating.value).toBe(0.5);
        expect(result.rating.name).toBe('ok');
        expect(result.ratedAt).toBe('2017-03-22T16:54:37.168975Z');
        expect(result.fullUserName).toBe('Tom Jones');
    });

    it('convert and parse ratings with empty user names', () => {
        const data = {
            ratedAt: '2017-03-22T16:54:32.168975Z',
            rating: 1.0,
            relativeRatedAt: '',
            translations: {
                de: {
                    comment: 'blah',
                },
            },
            user: {
                firstName: '',
                lastName: ' ',
            },
        };

        const result = convertRating(data, 'de');

        expect(result.fullUserName).toBe('Anonymous');
        expect(result.rating.value).toBe(1.0);
        expect(result.rating.name).toBe('good');
    });

    it('convert and parse bad rating', () => {
        const data = {
            ratedAt: '2017-03-22T16:54:32.168975Z',
            rating: 0.0,
            relativeRatedAt: '',
            translations: {
                de: {
                    comment: 'blah',
                },
            },
            user: {
                firstName: '',
                lastName: ' ',
            },
        };

        const result = convertRating(data, 'de');

        expect(result.rating.value).toBe(0.0);
        expect(result.rating.name).toBe('bad');
    });

});
