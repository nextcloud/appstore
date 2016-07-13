(function (global) {
    'use strict';


    class ImageSlider {
        constructor(logic, el) {
            this.logic = logic;
            this.logic.registerObserver(this);
            this.elem = el;
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
            window.addEventListener('resize', () => {
                this._setSlide(this.logic.curSlide);
            });
        }

        notify() {
            this._setSlide(this.logic.curSlide);
        }

        _setSlide(slide) {
            let imgSpacing = 4;
            let imgWidth = this.view.offsetWidth + imgSpacing;
            let curHeight = this.images[slide].offsetHeight;
            this.view.style.height = (curHeight - 1) + 'px';
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

            this.elem = document.createElement('div');
            this.elem.className = 'fullscreen';

            this.controls = slider.controls.cloneNode(true);
            this.controls.querySelector('.slider-nav').innerHTML = '';
            this.elem.appendChild(this.controls);

            this.contentArea = document.createElement('div');
            this.contentArea.className = 'content-area';
            this.elem.appendChild(this.contentArea);

            this.imgWrap = document.createElement('div');
            this.imgWrap.className = 'img-wrap';
            this.contentArea.appendChild(this.imgWrap);

            document.querySelector('body').appendChild(this.elem);

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
            this.elem.addEventListener('click', () => {
                this._close();
            });
            document.addEventListener('keydown', (ev) => {
                if ("key" in ev) {
                    if (ev.key == "Escape") this._close();
                } else {
                    if (ev.keyCode == 27) this._close();
                }
            });
            window.addEventListener('resize', () => {
                this._resizeImg();
            })
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
            this.imgWrap.innerHTML = '<img class="img" src="' + url + '"></img><a class="close-fullscreen-btn"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span></a>';

            let img = this.imgWrap.querySelector('.img');
            img.addEventListener('click', (ev) => {
                this.logic.increment(1);
                ev.stopPropagation();
            });
            this.imgWrap.querySelector('.close-fullscreen-btn').addEventListener('click', () => {
                this._close();
            });

            this._resizeImg();
            this._setActiveNav(slide);
        }

        _resizeImg() {
            let cArea = this.contentArea;
            let wrap = this.imgWrap;
            let img = wrap.querySelector('.img');

            // reset previously set size
            img.style.height = '';
            img.style.width = '';

            let padding = 60;
            let cAreaHeight = cArea.offsetHeight - padding;
            let cAreaWidth = cArea.offsetWidth - padding;
            let cAreaRatio = cAreaWidth / cAreaHeight;

            let imgRatio = img.offsetWidth / img.offsetHeight;

            // resize img
            if (imgRatio < cAreaRatio && img.offsetHeight > cAreaHeight) {
                // img is taller than cArea
                img.style.height = cAreaHeight + 'px';
                img.style.width = (imgRatio * img.offsetHeight) + 'px';
            } else if (imgRatio > cAreaRatio && img.offsetWidth > cAreaWidth) {
                // img is wider than cArea
                img.style.width = cAreaWidth + 'px';
                img.style.height = (img.offsetWidth / imgRatio) + 'px';
            }
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
            this.elem.remove()
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


    // init image slider
    let imgEls = Array.from(document.querySelectorAll('.img-slider .img'));
    let imgURLs = imgEls.map((img) => {
        return img.src;
    });

    if (imgURLs.length > 0) {
        let firstImg = new Image();
        firstImg.addEventListener('load', () => {
            let sliderLogic = new SliderLogic(imgURLs, 0);
            let imgSlider = new ImageSlider(sliderLogic, document.querySelector('.img-slider'));
        });
        firstImg.src = imgURLs[0];
    }


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
