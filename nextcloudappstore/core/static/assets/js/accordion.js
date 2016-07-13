(function (window) {
    'use strict';


    class AccordionItem {
        constructor(el) {
            this.el = el
            this.title = el.querySelector('.accordion-title');
            this.content = el.querySelector('.accordion-content');

            if (this._hasClassOpen()) this._setOpen(true);
            else this._setOpen(false);

            this.title.addEventListener('click', () => {
                this._toggle();
            });
        }

        _hasClassOpen() {
            return (' ' + this.el.className + ' ').indexOf(' open ') > -1;
        }

        _toggle() {
            if (this.open) this._setOpen(false);
            else this._setOpen(true);
        }

        _setOpen(boolean) {
            if(!boolean) {
                this.content.style.display = 'none';
                this.el.className = String(this.el.className).replace(' open', '');
            } else {
                this.content.style.display = '';
                if (!this._hasClassOpen()) this.el.className += ' open';
            }
            this.open = boolean;
        }
    }


    let items = Array.from(document.querySelectorAll('.accordion-item'));
    items = items.map((item) => {
        new AccordionItem(item);
    });

}(this));
