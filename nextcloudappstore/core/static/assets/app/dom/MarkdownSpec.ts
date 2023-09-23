import {renderMd} from './Markdown';

describe('Markdown rendering', () => {

    it('should render Markdown', () => {
        const md = '[link](http://google.com)\n```js\nalert(1);\n```';
        const expected = '<p>' +
            '<a href="http://google.com" rel="noopener noreferrer">link</a>' +
            '</p>\n' +
            '<pre><code class="language-js">' +
            '<span class="hljs-title function_">alert</span>(<span class="hljs-number">' +
            '1</span>);\n</code></pre>';
        expect(renderMd(md).trim()).toEqual(expected.trim());
    });

});
