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
                                    rating: IRating, lang: string, fallbackLang: string): HTMLElement {
    const root = render(template, {});
    if (!rating.appeal) {
        // Remove these buttons from template if comment has no appeal for spam
        const buttonsToRemove = [
            'button.comment-actions__delete',
            'button.comment-actions__appeal_cancel',
            'button.comment-actions__appeal_cancel_admin',
        ];
        buttonsToRemove.forEach((buttonSelector) => {
            try {
                const button = queryOrThrow(buttonSelector, HTMLButtonElement, root);
                root.removeChild(button);
            } catch {
                // Ignoring
            }
        });
    } else {
        try {
            const appealButton = queryOrThrow('button.comment-actions__appeal', HTMLButtonElement, root);
            root.removeChild(appealButton);
        } catch {
            // Ignoring
        }
    }
    // Init event listeners for comment actions buttons
    const commentActions = queryAll('.comment-actions-button', root);
    commentActions.forEach((commentActionButton: HTMLButtonElement) => {
        commentActionButton.addEventListener('click', () => {
            const token = queryOrThrow('input[name="csrfmiddlewaretoken"]', HTMLInputElement, root)?.value;
            const url = queryOrThrow('input[name="comment-action-url"]', HTMLInputElement, root)?.value;
            const reloadWithRatingParams = (deleteAction = false) => {
                const targetLang = !deleteAction ? lang : fallbackLang;
                const params = `comment_id=${rating.id}&bad_comment_lang=${targetLang}`;
                window.location.href = !deleteAction ?
                    window.location.pathname + '?' + params :
                    window.location.pathname;
            };
            if (commentActionButton.classList.contains('comment-actions__delete')) {
                deleteRating(url, token, rating, false).then(() => reloadWithRatingParams(true));
            } else if (commentActionButton.classList.contains('comment-actions__appeal')) {
                appealRating(url, token, rating).then(() => reloadWithRatingParams());
            } else if (commentActionButton.classList.contains('comment-actions__appeal_cancel')) {
                appealRating(url, token, rating, false).then(() => reloadWithRatingParams());
            } else if (commentActionButton.classList.contains('comment-actions__appeal_cancel_admin')) {
                deleteRating(url, token, rating, true).then(() => reloadWithRatingParams(true));
            }
        });
    });
    return root;
}

export function renderEmptyRatings(template: HTMLTemplateElement): HTMLElement {
    return render(template, {});
}
