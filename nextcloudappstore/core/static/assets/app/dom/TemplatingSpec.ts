import {noReferrerLinks} from './Templating';

describe('HTML templating utilities', () => {

    it('should add rel="noreferrer noopener"', () => {
        const html = 'Lorem <a href="#">ipsum dolor</a> sit amet, <a href="http://example.com">consectetur <strong>adipiscing</strong></a> elit. Praesent feugiat mauris <a href="http://example.com" target="_blank">non dapibus mattis</a>. Nunc luctus, lacus vitae.';
        const expected = 'Lorem <a href="#" rel="noopener noreferrer">ipsum dolor</a> sit amet, <a href="http://example.com" rel="noopener noreferrer">consectetur <strong>adipiscing</strong></a> elit. Praesent feugiat mauris <a href="http://example.com" target="_blank" rel="noopener noreferrer">non dapibus mattis</a>. Nunc luctus, lacus vitae.';
        expect(noReferrerLinks(html)).toEqual(expected);
    });

});
