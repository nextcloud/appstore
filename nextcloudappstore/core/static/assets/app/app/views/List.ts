import {queryForm} from '../../dom/Facades';
import {AppListForm} from '../forms/AppListForm';

window.onload = () => {
    const elem = queryForm('#filter-form');
    const form = new AppListForm(elem);
    form.attachEventListeners();
};
