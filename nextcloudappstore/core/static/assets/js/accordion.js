(function (global) {
    'use strict';

    const document = global.document;

    class AccordionItem {
        constructor(elem) {
            this.elem = elem;
            this.title = elem.querySelector('.accordion-title');
            this.content = elem.querySelector('.accordion-content');
            this._setOpen(this._isOpen());
            this.title.addEventListener('click', () => {
                this._toggle();
            });
        }

        _isOpen() {
            return this.elem.classList.contains('open');
        }

        _toggle() {
            this._setOpen(!this._isOpen());
        }

        _setOpen(isOpen) {
            if (isOpen) {
                this.content.style.display = '';
                this.elem.classList.add('open');
            } else {
                this.content.style.display = 'none';
                this.elem.classList.remove('open');
            }
        }
    }

    Array.from(document.querySelectorAll('.accordion-item'))
        .forEach((item) => new AccordionItem(item));

}(this));
