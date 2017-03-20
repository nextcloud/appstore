import {toHtml} from '../dom/Facades';
import {scanForm} from './HtmlForm';

const validForm = `
<form>
    <p class="global-error-msg">error</p>
    <p class="global-success-msg">success</p>
    
    <input name="test-input">
    <p class="error-msg-test-input"></p>
    
    <select name="test-select"></select>
    <p class="error-msg-test-select"></p>
    
    <textarea name="test-textarea"></textarea>
    <p class="error-msg-test-textarea"></p>
    
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
            expect(form.globalErrorMessage.innerText).toBe('error');
            expect(form.globalSuccessMessage.innerText).toBe('success');
            expect(form.submit.name).toBe('test-submit');
        } else {
            fail('Form is null');
        }
    });

});
