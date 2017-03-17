import {getMetaValue, testDom} from './Facades';

describe('DOM Facades', () => {

    it('should find no meta values', () => {
        const tpl = `<meta name="tests" content="value">`;
        testDom('head', tpl, () => expect(getMetaValue('test')).toBeNull());
    });

    it('should find meta values', () => {
        const tpl = `<meta name="test" content="value">`;
        testDom('head', tpl, () => expect(getMetaValue('test')).toBe('value'));
    });

});
