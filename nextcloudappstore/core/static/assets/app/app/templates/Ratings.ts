import {appealRating, deleteRating, IRating} from '../../api/Ratings';
import {renderMd} from '../../dom/Markdown';
import {render, Unescaped} from '../../dom/Templating';
import {queryAll, queryOrThrow} from '../../dom/Facades';

export function renderRating(template: HTMLTemplateElement,
                             rating: IRating): HTMLElement {
    const context = {
        '.author': rating.fullUserName,
        '.comment': new Unescaped(renderMd(rating.comment)),
        '.date': rating.relativeRatedAt,
    };

    const root = render(template, context);
    root.id = `rating-${rating.id}`; // Set the id attribute
    root.classList.add(rating.rating.name);
    return root;
}

export function renderRatingActions(template: HTMLTemplateElement,
                             rating: IRating): HTMLElement {
    const root = render(template, {});
    if (!rating.appeal) {
        // Remove delete button if comment has no appeal for spam
        try {
            const deleteButton = queryOrThrow('button.comment-actions__delete', HTMLButtonElement, root);
            root.removeChild(deleteButton);
        } catch {
          // Nothing to do, if user not admin - no delete button
        }
    }
    // Init event listeners for buttons
    const commentActions = queryAll('.comment-actions-button', root);
    commentActions.forEach((commentActionButton: HTMLButtonElement) => {
        commentActionButton.addEventListener('click', () => {
            const token = queryOrThrow('input[name="csrfmiddlewaretoken"]', HTMLInputElement, root)?.value;
            const url = queryOrThrow('input[name="comment-action-url"]', HTMLInputElement, root)?.value;
            if (commentActionButton.classList.contains('comment-actions__delete')) {
                deleteRating(url, token, rating);
            } else if (commentActionButton.classList.contains('comment-actions__appeal')) {
                appealRating(url, token, rating);
            }
        });
    });
    return root;
}

export function renderEmptyRatings(template: HTMLTemplateElement): HTMLElement {
    return render(template, {});
}
