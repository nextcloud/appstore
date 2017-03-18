import {queryForm, ready} from '../../dom/Facades';
import {AppListForm} from '../forms/AppListForm';

ready(() => {
    const elem = queryForm('#filter-form');
    const form = new AppListForm(elem);
    form.attachEventListeners();
});
