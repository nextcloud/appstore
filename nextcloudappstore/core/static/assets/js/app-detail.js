(function (global) {
    'use strict';


    class ImageSlider {
        constructor(logic, el) {
            this.logic = logic;
            this.logic.registerObserver(this);
            this.el = el;
            this.view = el.querySelector('.img-slider-view');
            this.strip = el.querySelector('.img-slider-view .img-strip');
            this.controls = el.querySelector('.img-slider-controls');
            this.nav = el.querySelector('.slider-nav');
            this.navBtns = this._generateButtons();
            this.images = Array.from(el.querySelectorAll('.img'));
            this._setSlide(this.logic.curSlide);

            el.querySelector('.next').addEventListener('click', () => {
                this.logic.increment(1);
            });
            el.querySelector('.prev').addEventListener('click', () => {
                this.logic.increment(-1);
            });
            el.querySelector('.fullscreen-btn').addEventListener('click', () => {
                this._openFullscreen();
            });
        }

        notify() {
            this._setSlide(this.logic.curSlide);
        }

        _setSlide(slide) {
            let imgSpacing = 4;
            let imgWidth = this.view.offsetWidth + imgSpacing;
            let curHeight = this.images[slide].offsetHeight;
            this.view.style.height = curHeight + 'px';
            this.strip.style.right = (imgWidth * slide) + 'px';
            this._setActiveNav(slide);
        }

        _setActiveNav(index) {
            this.navBtns.forEach(function(btn) {
                btn.style.opacity = '';
            });
            this.navBtns[index].style.opacity = 1;
        }

        _generateButtons() {
            let btns = [];
            for (let i = 0; i < this.logic.imgCount(); i++) {
                let btn = document.createElement('a');
                btn.addEventListener('click', () => {
                    this.logic.setSlide(i);
                });
                this.nav.appendChild(btn);
                btns.push(btn);
            }
            return btns;
        }

        _openFullscreen() {
            let fullscreen = new Fullscreen(this.logic, this);
        }
    }

    class Fullscreen {
        constructor(logic, slider) {

            // Create elements
            this.logic = logic;
            this.logic.registerObserver(this);

            this.el = document.createElement('div');
            this.el.className = 'fullscreen';

            this.controls = slider.controls.cloneNode(true);
            this.controls.querySelector('.slider-nav').innerHTML = '';
            this.el.appendChild(this.controls);

            this.closeBtn = slider.el.querySelector('.close-fullscreen-btn').cloneNode(true);
            this.el.appendChild(this.closeBtn);

            this.imgWrap = document.createElement('div');
            this.imgWrap.className = 'img-wrap';
            this.el.appendChild(this.imgWrap);

            document.querySelector('body').appendChild(this.el);

            // Setup
            this.navBtns = this._generateButtons();
            this._setSlide(this.logic.curSlide);
            this._showScrollbar(false);
            this.controls.querySelector('.next').addEventListener('click', (ev) => {
                this.logic.increment(1);
                ev.stopPropagation();
            });
            this.controls.querySelector('.prev').addEventListener('click', (ev) => {
                this.logic.increment(-1);
                ev.stopPropagation();
            });
            this.controls.addEventListener('click', (ev) => {
                ev.stopPropagation();
            });
            this.el.addEventListener('click', () => {
                this._close();
            });
            this.closeBtn.addEventListener('click', () => {
                this._close();
            });
            document.addEventListener('keydown', (ev) => {
                if ("key" in ev) {
                    if (ev.key == "Escape") this._close();
                } else {
                    if (ev.keyCode == 27) this._close();
                }
            });
        }

        _generateButtons() {
            let btns = [];
            for (let i = 0; i < this.logic.imgCount(); i++) {
                let btn = document.createElement('a');
                btn.addEventListener('click', (ev) => {
                    this.logic.setSlide(i);
                    ev.stopPropagation();
                });
                this.controls.querySelector('.slider-nav').appendChild(btn);
                btns.push(btn);
            }
            return btns;
        }

        _setSlide(slide) {
            let url = this.logic.imgURLs[this.logic.curSlide];
            this.imgWrap.innerHTML = '<img class="img" src="' + url + '">';

            let img = this.imgWrap.querySelector('.img');
            let imgRatio = img.offsetWidth / img.offsetHeight;
            let padding = 60;
            let wrapHeight = this.imgWrap.offsetHeight - padding;
            let wrapWidth = this.imgWrap.offsetWidth - padding;
            let wrapRatio = wrapWidth / wrapHeight;

            if (imgRatio < wrapRatio && img.offsetHeight > wrapHeight) {
                img.style.height = wrapHeight + 'px';
                img.style.width = (imgRatio * img.offsetHeight) + 'px';
            } else if (imgRatio > wrapRatio && img.offsetWidth > wrapWidth) {
                img.style.width = wrapWidth + 'px';
                img.style.height = (img.offsetWidth / imgRatio) + 'px';
            }

            img.addEventListener('click', (ev) => {
                this.logic.increment(1);
                ev.stopPropagation();
            });

            this._setActiveNav(slide);
        }

        _setActiveNav(index) {
            this.navBtns.forEach(function(btn) {
                btn.style.opacity = '';
            });
            this.navBtns[index].style.opacity = 1;
        }

        notify() {
            this._setSlide(this.logic.curSlide);
        }

        _showScrollbar(boolean) {
            let body = document.querySelector('body');
            if (!boolean) body.style.overflow = 'hidden';
            else body.style.overflow = '';
        }

        _close() {
            this._showScrollbar(true);
            this.el.remove()
            delete this;
        }
    }


    class SliderLogic {
        constructor(imgURLs, initSlide) {
            this.imgURLs = imgURLs;
            this.curSlide = initSlide;
            this.observers = [];
        }

        imgCount() {
            return this.imgURLs.length;
        }

        setSlide(index) {
            this.curSlide = index;
            this._notifyObservers();
        }

        increment(steps) {
            let imgCount = this.imgCount();
            let next = this.curSlide + steps;
            next = ((next % imgCount) + imgCount) % imgCount; // because a simple % does it wrong
            this.setSlide(next);
        }

        registerObserver(view) {
            this.observers.push(view);
        }

        _notifyObservers() {
            this.observers.forEach((obs) => {
                obs.notify();
            });
        }
    }


    let document = global.document;
    let hljs = global.hljs;
    let md = global.markdownit({
        highlight: function (str, lang) {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(lang, str).value;
                } catch (__) {}
            }

            return ''; // use external default escaping
        }
    });


    let imgEls = Array.from(document.querySelectorAll('.img-slider .img'));
    let imgURLs = imgEls.map((img) => {
        return img.src;
    });

    let sliderLogic = new SliderLogic(imgURLs, 0);
    let imgSlider = new ImageSlider(sliderLogic, document.querySelector('.img-slider'));

    // create markdown for app description
    let appDescriptionUrl = document.querySelector('meta[name="nextcloudappstore-app-detail-url"]');
    let descriptionTarget = document.querySelector('.app-description');
    fetch(appDescriptionUrl.content).then((response) => {
        return response.text()
    }).then((description) => {
        descriptionTarget.classList.remove('loading');
        descriptionTarget.innerHTML = md.render(description);
    });
}(this));
