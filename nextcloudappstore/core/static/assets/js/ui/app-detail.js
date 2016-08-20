(function (global) {
    'use strict';

    let document = global.document;
    let hljs = global.hljs;
    let md = global.markdownit({
        highlight: function (str, lang) {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(lang, str).value;
                } catch (__) {
                }
            }
            return ''; // use external default escaping
        }
    });

    // init image slider
    let imgEls = Array.from(document.querySelectorAll('.img-slider .img'));
    let imgURLs = imgEls.map((img) => img.src);

    if (imgURLs.length > 0) {
        let firstImg = new Image();
        firstImg.addEventListener('load', () => {
            let sliderLogic = new global.SliderLogic(imgURLs, 0);
            new global.ImageSlider(sliderLogic, document.querySelector('.img-slider'));
        });
        firstImg.src = imgURLs[0];
    }

    // create markdown for app description
    let appDescriptionUrl = document.querySelector('meta[name="nextcloudappstore-app-detail-url"]');
    let descriptionTarget = document.querySelector('.app-description');
    fetch(appDescriptionUrl.content).then((response) => response.text())
        .then((description) => {
            descriptionTarget.classList.remove('loading');
            descriptionTarget.innerHTML = global.noReferrerLinks(md.render(description));
        });
}(this));
