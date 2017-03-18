import {queryForm} from '../../dom/Facades';
import {AppListForm} from '../forms/AppListForm';

export function main() {
    const elem = queryForm('#filter-form');
    const form = new AppListForm(elem);
    form.attachEventListeners();
}
