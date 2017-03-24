import {queryOrThrow, ready} from '../../dom/Facades';
import {scanForm} from '../../forms/HtmlForm';
import {scanTranslations, Translator} from '../../l10n/Translator';
import {AppUploadForm} from '../forms/AppUploadForm';

ready().then(() => {
    const formElement = queryOrThrow<HTMLFormElement>('#app-upload-form');
    const formMeta = scanForm(formElement);
    const translations = scanTranslations(formElement);
    const translator = new Translator(translations);
    const form = new AppUploadForm(formMeta, translator);
});
