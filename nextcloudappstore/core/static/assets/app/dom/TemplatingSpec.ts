import {testDom} from './Facades';
import {noReferrerLinks, render} from './Templating';

describe('HTML templating utilities', () => {

    it('should add rel="noreferrer noopener"', () => {
        const html = 'Lorem <a href="#">ipsum </a> sit';
        const expected =
            'Lorem <a href="#" rel="noopener noreferrer">ipsum </a> sit';
        expect(noReferrerLinks(html)).toEqual(expected);
    });

    it('should evaluate a template', () => {
        const tpl = `<template><p><span></span></p></template>`;
        const expected = `<p class="test"><span>&lt;a href="as"&gt;&lt;/a` +
            `&gt;</span></p>`;
        testDom('body', HTMLBodyElement, tpl,
            (elem: HTMLTemplateElement) => {
                const result = render(elem, {span: '<a href="as"></a>'});
                result.classList.add('test');
                const tmp = document.createElement('div');
                tmp.appendChild(result);
                expect(tmp.innerHTML).toEqual(expected);
            });
    });

});
