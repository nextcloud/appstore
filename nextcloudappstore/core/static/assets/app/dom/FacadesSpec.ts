import {DomElementDoesNotExist} from './DomElementDoesNotExist';
import {getMetaValue, queryOrThrow, testDom} from './Facades';

describe('DOM Facades', () => {

    it('should find no meta values', () => {
        const tpl = `<meta name="tests" content="value">`;
        testDom('head', tpl, () => expect(getMetaValue('test')).toBeNull());
    });

    it('should find meta values', () => {
        const tpl = `<meta name="test" content="value">`;
        testDom('head', tpl, () => expect(getMetaValue('test')).toBe('value'));
    });

    it('should throw if no element is found', () => {
        const tpl = `<link>`;
        testDom('head', tpl, () => {
            const msg = 'No element found for selector test';
            expect(() => queryOrThrow('test'))
                .toThrow(new DomElementDoesNotExist(msg));
        });
    });

    it('should not throw if element is found', () => {
        const tpl = `<meta name="test" content="value">`;
        testDom('head', tpl, () => {
            const msg = 'No element found for selector meta';
            expect(() => queryOrThrow('meta'))
                .not.toThrow(new DomElementDoesNotExist(msg));
        });
    });

});
