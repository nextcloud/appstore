import {AjaxForm} from '../../forms/AjaxForm';
import {HtmlForm} from '../../forms/HtmlForm';
import {IValidator} from '../../forms/validators/IValidator';
import {Translator} from '../../l10n/Translator';

export class AppRegisterForm extends AjaxForm {

    constructor(form: HtmlForm,
                validators: Map<string, IValidator[]>,
                translator: Translator) {
        super(form, validators, translator);
    }

}
