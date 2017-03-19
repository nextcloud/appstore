import * as moment from 'moment';
import {apiRequest, pageRequest} from '../../api/Request';
import {id} from '../../dom/Facades';
import {renderMd} from '../../dom/Markdown';
import {escapeHtml} from '../../dom/Templating';

/* tslint:disable */
declare global {
    interface Window {
        renderMd: (html: string) => string;
        moment: any;
        apiRequest: any;
        pageRequest: any;
        escapeHtml: any;
        id: any;
    }
}

window.renderMd = renderMd;
window.moment = moment;
window.pageRequest = pageRequest;
window.apiRequest = apiRequest;
window.escapeHtml = escapeHtml;
window.id = id;
/* tslint:enable */
