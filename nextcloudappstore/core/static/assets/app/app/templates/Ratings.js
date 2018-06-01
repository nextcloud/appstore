import { renderMd } from '../../dom/Markdown';
import { render, Unescaped } from '../../dom/Templating';
export function renderRating(template, rating) {
    const context = {
        '.author': rating.fullUserName,
        '.comment': new Unescaped(renderMd(rating.comment)),
        '.date': rating.relativeRatedAt,
    };
    const root = render(template, context);
    root.classList.add(rating.rating.name);
    return root;
}
export function renderEmptyRatings(template) {
    return render(template, {});
}
//# sourceMappingURL=Ratings.js.map