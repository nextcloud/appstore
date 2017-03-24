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
        const tpl = `<template><span><p></p></span></template>`;
        const expected = `<span class="test"><p>&lt;hi alt="as"&gt;</p></span>`;
        testDom('body', tpl, (elem: HTMLTemplateElement) => {
            const result = render(elem, {p: '<hi alt="as">'});
            result.classList.add('test');
            const tmp = document.createElement('div');
            tmp.appendChild(result);
            expect(tmp.innerHTML).toEqual(expected);
        });
    });

});
