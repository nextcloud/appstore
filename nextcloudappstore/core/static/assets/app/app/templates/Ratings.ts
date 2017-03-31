import * as moment from 'moment';
import {IRating} from '../../api/Ratings';
import {renderMd} from '../../dom/Markdown';
import {render, Unescaped} from '../../dom/Templating';

export function renderRating(template: HTMLTemplateElement,
                             rating: IRating, lang: string): HTMLElement {
    const context = {
        '.author': rating.fullUserName,
        '.comment': new Unescaped(renderMd(rating.comment)),
        '.date': moment(rating.ratedAt).locale(lang).fromNow(),
    };

    const root = render(template, context);
    root.classList.add(rating.rating.name);
    return root;
}

export function renderEmptyRatings(template: HTMLTemplateElement): HTMLElement {
    return render(template, {});
}
