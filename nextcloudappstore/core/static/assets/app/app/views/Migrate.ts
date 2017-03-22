import {fetchDescription} from '../../api/Api';
import {fetchRatings} from '../../api/Ratings';
import {id} from '../../dom/Facades';
import {renderEmptyRatings, renderRating} from '../templates/Ratings';

/* tslint:disable */
declare global {
    interface Window {
        id: any;
        fetchRatings: any;
        fetchDescription: any;
        renderRating: any;
        renderEmptyRatings: any;
    }
}

window.id = id;
window.fetchRatings = fetchRatings;
window.fetchDescription = fetchDescription;
window.renderRating = renderRating;
window.renderEmptyRatings = renderEmptyRatings;
/* tslint:enable */
