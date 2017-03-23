(function (global) {
    'use strict';

    function load_comments(languageCode) {
        fetchRatings(ratingUrl, languageCode, fallbackLang)
            .then((result) => {
                ratingContainer.classList.remove('loading');
                ratingContainer.innerHTML = '';
                commentLangInput.value = result.lang;

                if (result.ratings.length > 0) {
                    result.ratings.forEach((rating) => {
                        const tpl = renderRating(ratingTpl, rating, result.lang);
                        ratingContainer.appendChild(tpl);
                    });
                } else {
                    const tpl = renderEmptyRatings(noRatingTpl);
                    ratingContainer.appendChild(tpl);
                }
            });
    }

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

    languageInput.addEventListener('change', (event) => {
        const lang = event.target.value;
        commentInput.readOnly = true;
        fetchRatings(ratingUrl + "?current_user=true&lang=" + lang, lang)
            .then((result) => {
                let value = '';
                let ratings = result.ratings;
                if (ratings.length > 0) {
                    value = ratings[0].comment;
                }
                commentInput.value = value;
                commentInput.readOnly = false;
            }).catch(() => commentInput.readOnly = false);
    });

    commentLangInput.addEventListener('change', (event) => {
        load_comments(event.target.value);
    });

    load_comments(currentLang);
}(this));
