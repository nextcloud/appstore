import * as Blazy from 'blazy';
import {queryOrThrow, ready} from '../../dom/Facades';
import {findFormFields, FormField} from '../../forms/HtmlForm';
import {Maybe} from '../../Utils';

ready.then(() => {
    const form = queryOrThrow('#filter-form', HTMLFormElement);
    const fields = findFormFields(form);
    fields.forEach((elem: FormField) => {
        elem.addEventListener('change', () => {
            form.submit();
        });
    });
    // tslint:disable-next-line no-unused-expression
    new Blazy({
        container: '#container',
        success: (elem) => {
            new Maybe(elem.closest('.app-list-screenshot'))
                .ifPresent((el) => el.classList.remove('center'));
        },
    });
});
