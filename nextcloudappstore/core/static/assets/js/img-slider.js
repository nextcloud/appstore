(function (global) {
    'use strict';

    const document = global.document;


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
            this.controls.querySelector('.next')
                .addEventListener('click', (ev) => {
                    this.logic.increment(1);
                    ev.stopPropagation();
                });
            this.controls.querySelector('.prev')
                .addEventListener('click', (ev) => {
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
                if ('key' in ev) {
                    if (ev.key === 'Escape') {
                        this._close();
                    }
                } else {
                    if (ev.keyCode === 27) {
                        this._close();
                    }
                }
            });
            window.addEventListener('resize', () => {
                this._resizeImg();
            });
        }

        _generateButtons() {
            const btns = [];
            const createListener = (index) => {
                return (ev) => {
                    this.logic.setSlide(index);
                    ev.stopPropagation();
                };
            };
            for (let i = 0; i < this.logic.imgCount(); i++) {
                const btn = document.createElement('a');
                btn.addEventListener('click', createListener(i));
                this.controls.querySelector('.slider-nav').appendChild(btn);
                btns.push(btn);
            }
            return btns;
        }

        _setSlide(slide) {
            const url = this.logic.imgURLs[this.logic.curSlide];
            this.imgWrap.innerHTML = '<img class="img" src="' + url + '">' +
                '<a class="close-fullscreen-btn">' +
                '<span class="glyphicon glyphicon-remove" aria-hidden="true">' +
                '</span></a>';

            const img = this.imgWrap.querySelector('.img');
            img.addEventListener('click', (ev) => {
                this.logic.increment(1);
                ev.stopPropagation();
            });
            this.imgWrap.querySelector('.close-fullscreen-btn')
                .addEventListener('click', () => {
                    this._close();
                });

            this._resizeImg();
            this._setActiveNav(slide);
        }

        _resizeImg() {
            const cArea = this.contentArea;
            const wrap = this.imgWrap;
            const img = wrap.querySelector('.img');

            // reset previously set size
            img.style.height = '';
            img.style.width = '';

            const padding = 60;
            const cAreaHeight = cArea.offsetHeight - padding;
            const cAreaWidth = cArea.offsetWidth - padding;
            const cAreaRatio = cAreaWidth / cAreaHeight;

            const imgRatio = img.offsetWidth / img.offsetHeight;

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
            this.navBtns.forEach(function (btn) {
                btn.style.opacity = '';
            });
            this.navBtns[index].style.opacity = 1;
        }

        notify() {
            this._setSlide(this.logic.curSlide);
        }

        _showScrollbar(isShowScrollbar) {
            const body = document.querySelector('body');
            if (!isShowScrollbar) {
                body.style.overflow = 'hidden';
            } else {
                body.style.overflow = '';
            }
        }

        _close() {
            this._showScrollbar(true);
            this.elem.remove();
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
            const imgCount = this.imgCount();
            let next = this.curSlide + steps;
            // because a simple % does it wrong
            next = ((next % imgCount) + imgCount) % imgCount;
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

            el.querySelector('.next')
                .addEventListener('click', () => {
                    this.logic.increment(1);
                });
            el.querySelector('.prev')
                .addEventListener('click', () => {
                    this.logic.increment(-1);
                });
            el.querySelector('.fullscreen-btn')
                .addEventListener('click', () => {
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
            const imgSpacing = 4;
            const imgWidth = this.view.offsetWidth + imgSpacing;
            const curHeight = this.images[slide].offsetHeight;
            this.view.style.height = (curHeight - 1) + 'px';
            this.strip.style.right = (imgWidth * slide) + 'px';
            this._setActiveNav(slide);
        }

        _setActiveNav(index) {
            this.navBtns.forEach(function (btn) {
                btn.style.opacity = '';
            });
            this.navBtns[index].style.opacity = 1;
        }

        _generateButtons() {
            const btns = [];
            const createListener = (index) => {
                return () => {
                    this.logic.setSlide(index);
                };
            };
            for (let i = 0; i < this.logic.imgCount(); i++) {
                const btn = document.createElement('a');
                btn.addEventListener('click', createListener(i));
                this.nav.appendChild(btn);
                btns.push(btn);
            }
            return btns;
        }

        _openFullscreen() {
            new Fullscreen(this.logic, this);
        }
    }

    global.ImageSlider = ImageSlider;
    global.SliderLogic = SliderLogic;

}(this));
