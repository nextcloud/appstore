export class Accordion {
    private title: HTMLElement;
    private content: HTMLElement;

    constructor(private elem: HTMLElement) {
        const title = elem.querySelector('.accordion-title') as HTMLElement;
        const content = elem.querySelector('.accordion-content') as HTMLElement;
        if (title === null || content === null) {
            throw new Error(`No content or title found for elem ${elem}`);
        }
        this.title = title;
        this.content = content;
    }

    public attachEventListeners() {
        this.title.addEventListener('click', this.toggle.bind(this));
    }

    private isOpen(): boolean {
        return this.elem.classList.contains('open');
    }

    private toggle() {
        if (this.isOpen()) {
            this.content.style.display = 'none';
            this.elem.classList.remove('open');
        } else {
            this.content.style.display = '';
            this.elem.classList.add('open');
        }
    }
}
