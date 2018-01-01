import {IRating} from '../../api/Ratings';
import {renderMd} from '../../dom/Markdown';
import {render, Unescaped} from '../../dom/Templating';

export function renderRating(template: HTMLTemplateElement,
                             rating: IRating): HTMLElement {
    const context = {
        '.author': rating.fullUserName,
        '.comment': new Unescaped(renderMd(rating.comment)),
        '.date': rating.relativeRatedAt,
    };

    const root = render(template, context);
    root.classList.add(rating.rating.name);
    return root;
}

export function renderEmptyRatings(template: HTMLTemplateElement): HTMLElement {
    return render(template, {});
}
