/**
 * SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import {appealRating, deleteRating, IRating, replyToRating} from '../../api/Ratings';
import {renderMd} from '../../dom/Markdown';
import {render, Unescaped} from '../../dom/Templating';
import {queryAll, queryOrThrow} from '../../dom/Facades';

export function renderRating(template: HTMLTemplateElement,
                             rating: IRating): HTMLElement {
    const context = {
        '.author': rating.fullUserName,
        '.comment': new Unescaped(renderMd(rating.comment)),
        '.comment-reply__date': rating.relativeRepliedAt,
        '.comment-reply__text': new Unescaped(renderMd(rating.reply)),
        '.date': rating.relativeRatedAt,
    };

    const root = render(template, context);
    root.id = `rating-${rating.id}`; // Set the id attribute
    root.classList.add(rating.rating.name);
    if (rating.reply === '') {
        queryAll('.comment-reply', root).forEach((reply) => reply.remove());
    }
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
    initReplyForm(root, rating, lang);

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
            } else if (commentActionButton.classList.contains('comment-actions__reply')) {
                const form = queryOrThrow('.comment-reply-form', HTMLFormElement, root);
                form.hidden = !form.hidden;
                if (!form.hidden) {
                    queryOrThrow('.comment-reply-form__text', HTMLTextAreaElement, form).focus();
                }
            }
        });
    });
    return root;
}

/**
 * Sets up the app owner's reply form, if the template contains one
 * @param root rendered comment actions
 * @param rating
 * @param lang language the comment list is shown in
 */
function initReplyForm(root: HTMLElement, rating: IRating, lang: string) {
    const form = root.querySelector<HTMLFormElement>('.comment-reply-form');
    if (form === null) {
        return;
    }
    const text = queryOrThrow('.comment-reply-form__text', HTMLTextAreaElement, form);
    const label = queryOrThrow('.comment-actions__reply-label', HTMLSpanElement, root);
    const deleteButton = queryOrThrow('.comment-reply-form__delete', HTMLButtonElement, form);
    text.value = rating.reply;
    if (rating.reply === '') {
        queryOrThrow('.comment-reply-form__delete-row', HTMLDivElement, form).remove();
    } else {
        label.innerText = label.dataset.editLabel || label.innerText;
    }

    const save = (reply: string) => {
        const token = queryOrThrow('input[name="csrfmiddlewaretoken"]', HTMLInputElement, root).value;
        const url = queryOrThrow('input[name="comment-action-url"]', HTMLInputElement, root).value;
        replyToRating(url, token, rating, reply).then(() => {
            const params = `comment_id=${rating.id}&bad_comment_lang=${lang}`;
            window.location.href = window.location.pathname + '?' + params;
        });
    };

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        save(text.value);
    });
    deleteButton.addEventListener('click', () => save(''));
    queryOrThrow('.comment-reply-form__cancel', HTMLButtonElement, form).addEventListener('click', () => {
        text.value = rating.reply;
        form.hidden = true;
    });
}

export function renderEmptyRatings(template: HTMLTemplateElement): HTMLElement {
    return render(template, {});
}
