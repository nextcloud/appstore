import {Form, FormField} from '../../form/Form';

export class AppListForm extends Form {

    constructor(form: HTMLFormElement) {
        super(form);
    }

    public attachEventListeners() {
        this.findFields()
            .forEach((elem: FormField, name: string) => {
                elem.addEventListener('change', () => {
                    this.form.submit();
                });
            });
    }

}
