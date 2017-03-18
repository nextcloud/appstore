import * as moment from 'moment';
import {ready} from '../../dom/Facades';
import {renderMd} from '../../dom/Markdown';

/* tslint:disable */
declare global {
    interface Window {
        renderMd: (html: string) => string;
        moment: any;
    }
}

ready(() => {
    // only load markdown for now so website does not fail
    window.renderMd = renderMd;
    window.moment = moment;
});
/* tslint:enable */
