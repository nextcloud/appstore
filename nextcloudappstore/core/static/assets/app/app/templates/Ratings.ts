import * as moment from 'moment';
import {Rating} from '../../api/Ratings';
import {queryAll} from '../../dom/Facades';
import {renderMd} from '../../dom/Markdown';
import {escapeHtml} from '../../dom/Templating';
import {TemplateEmpty} from './TemplateEmpty';

function findRoot(template: Node): HTMLElement {
    if (template.childNodes.length === 0) {
        throw new TemplateEmpty('Given template is empty');
    } else {
        return template.childNodes[1] as HTMLElement;
    }
}

type Context = {
    [selector: string]: string;
};

/**
 * Renders an HTML template
 * @param template the template dom element
 * @param context an object whose keys are selectors and values are ESCAPED
 * values to render to the document
 * @param transformer if given will be executed by passing in the root element
 */
function render(template: HTMLTemplateElement,
                context: Context,
                transformer?: (root: HTMLElement) => void): Node {
    const result = document.importNode(template.content, true);
    const root = findRoot(result);

    Object.keys(context).forEach((selector: string) => {
        queryAll(selector, root).forEach((element: HTMLElement) => {
            element.innerHTML = context[selector];
        });
    });

    if (transformer) {
        transformer(root);
    }

    return result;
}

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
