export function escapeHtml(text: string): string {
    const div = window.document.createElement('div');
    div.appendChild(window.document.createTextNode(text));
    return div.innerHTML;
}
