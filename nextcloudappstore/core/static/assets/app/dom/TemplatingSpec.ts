import {noReferrerLinks} from './Templating';

describe('HTML templating utilities', () => {

    it('should add rel="noreferrer noopener"', () => {
        const html = 'Lorem <a href="#">ipsum </a> sit';
        const expected =
            'Lorem <a href="#" rel="noopener noreferrer">ipsum </a> sit';
        expect(noReferrerLinks(html)).toEqual(expected);
    });

});
