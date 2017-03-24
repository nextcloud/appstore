import {queryOrThrow, ready} from '../../dom/Facades';
import {findFormFields, FormField} from '../../forms/HtmlForm';

ready().then(() => {
    const form = queryOrThrow<HTMLFormElement>('#filter-form');
    const fields = findFormFields(form);
    fields.forEach((elem: FormField) => {
        elem.addEventListener('change', () => {
            form.submit();
        });
    });
});
