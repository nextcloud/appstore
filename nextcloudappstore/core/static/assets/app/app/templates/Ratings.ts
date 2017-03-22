import * as moment from 'moment';
import {Rating} from '../../api/Ratings';
import {renderMd} from '../../dom/Markdown';
import {escapeHtml, render} from '../../dom/Templating';

export function renderRating(template: HTMLTemplateElement,
                             rating: Rating, lang: string): Node {
    const context = {
        '.author': escapeHtml(rating.fullUserName),
        '.comment': renderMd(rating.comment),
        '.date': escapeHtml(moment(rating.ratedAt).locale(lang).fromNow()),
    };

    return render(template, context, (root) => {
        root.classList.add(rating.rating.name);
    });
}

export function renderEmptyRatings(template: HTMLTemplateElement): Node {
    return render(template, {});
}
