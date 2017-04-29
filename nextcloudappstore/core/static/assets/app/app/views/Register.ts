import {idOrThrow, ready} from '../../dom/Facades';
import {scanForm} from '../../forms/HtmlForm';
import {CertValidator} from '../../forms/validators/CertValidator';
import {IValidator} from '../../forms/validators/IValidator';
import {scanTranslations, Translator} from '../../l10n/Translator';
import {AppRegisterForm} from '../forms/AppRegisterForm';

ready.then(() => {
    const formElement = idOrThrow('app-register-form', HTMLFormElement);
    const formMeta = scanForm(formElement);
    const validators = new Map<string, IValidator[]>();
    validators.set('certificate', [new CertValidator()]);
    const translations = scanTranslations(formElement);
    const translator = new Translator(translations);
    const form = new AppRegisterForm(formMeta, validators, translator);
    form.bindListeners();
});
