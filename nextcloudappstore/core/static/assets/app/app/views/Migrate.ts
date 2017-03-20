import * as moment from 'moment';
import {id} from '../../dom/Facades';
import {renderMd} from '../../dom/Markdown';
import {escapeHtml} from '../../dom/Templating';
import {createRatingClass} from '../Ratings';

/* tslint:disable */
declare global {
    interface Window {
        renderMd: (html: string) => string;
        moment: any;
        escapeHtml: any;
        id: any;
        createRatingClass: any;
    }
}

window.renderMd = renderMd;
window.moment = moment;
window.escapeHtml = escapeHtml;
window.id = id;
window.createRatingClass = createRatingClass;
/* tslint:enable */
