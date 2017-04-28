import {DomElementDoesNotExist} from './DomElementDoesNotExist';
import {getMetaValue, queryOrThrow, testDom} from './Facades';

describe('DOM Facades', () => {

    it('should find no meta values', () => {
        const tpl = `<meta name="tests" content="value">`;
        testDom('head', HTMLHeadElement, tpl,
            () => expect(getMetaValue('test').isPresent())
                .toBe(false));
    });

    it('should find meta values', () => {
        const tpl = `<meta name="test" content="value">`;
        testDom('head', HTMLHeadElement, tpl, () => {
            const result = getMetaValue('test');
            expect(result.isPresent()).toBe(true);
            result.ifPresent((value) => expect(value).toBe('value'));
        });
    });

    it('should throw if no element is found', () => {
        const tpl = `<link>`;
        testDom('head', HTMLHeadElement, tpl, () => {
            const msg = 'No element found for selector test';
            expect(() => queryOrThrow('test', HTMLLinkElement))
                .toThrow(new DomElementDoesNotExist(msg));
        });
    });

    it('should not throw if element is found', () => {
        const tpl = `<meta name="test" content="value">`;
        testDom('head', HTMLHeadElement, tpl, () => {
            const msg = 'No element found for selector meta';
            expect(() => queryOrThrow('meta', HTMLMetaElement))
                .not.toThrow(new DomElementDoesNotExist(msg));
        });
    });

});
