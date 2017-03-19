import {toHtml} from '../dom/Facades';
import {scanForm} from './HtmlForm';

const validForm = `
<form>
    <p class="global-msg"></p>
    
    <input name="test-input">
    <p class="msg-test-input"></p>
    
    <select name="test-select"></select>
    <p class="msg-test-select"></p>
    
    <textarea name="test-textarea"></textarea>
    <p class="msg-test-textarea"></p>
    
    <input type="hidden" name="hidden-input"/>
    <input type="submit" name="test-submit"/>
</form>
`;

describe('HTML form parsing', () => {

    it('should parse all fields', () => {
        const formHtml = toHtml<HTMLFormElement>(validForm);
        if (formHtml !== null) {
            const form = scanForm(formHtml);
            expect(form.fields.size).toBe(4);
            expect(form.messages.size).toBe(3);
            expect(form.submit.name).toBe('test-submit');
        } else {
            fail('Form is null');
        }
    });

});
