import * as moment from 'moment';
import {Rating} from '../../api/Ratings';
import {renderMd} from '../../dom/Markdown';
import {render, Unescaped} from '../../dom/Templating';

export function renderRating(template: HTMLTemplateElement,
                             rating: Rating, lang: string): Node {
    const context = {
        '.author': rating.fullUserName,
        '.comment': new Unescaped(renderMd(rating.comment)),
        '.date': moment(rating.ratedAt).locale(lang).fromNow(),
    };

    return render(template, context, (root) => {
        root.classList.add(rating.rating.name);
    });
}

export function renderEmptyRatings(template: HTMLTemplateElement): Node {
    return render(template, {});
}
