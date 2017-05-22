import * as Blazy from 'blazy';
import {queryAll, queryOrThrow, ready} from '../../dom/Facades';
import {findFormFields, FormField} from '../../forms/HtmlForm';

ready.then(() => {
    const form = queryOrThrow('#filter-form', HTMLFormElement);
    const fields = findFormFields(form);
    fields.forEach((elem: FormField) => {
        elem.addEventListener('change', () => {
            form.submit();
        });
    });
    // tslint:disable-next-lineno-unused-expression: false
    new Blazy({
        container: '#container',
        success: () => {
            queryAll('.app-list-screenshot')
                .forEach((el) => el.classList.remove('center'));
        },
    });
});
