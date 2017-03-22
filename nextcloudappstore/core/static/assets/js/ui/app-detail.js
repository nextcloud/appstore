(function (global) {
    'use strict';
    let document = global.document;
    let ratingUrl = document.querySelector('meta[name="nextcloudappstore-app-ratings-url"]').content;
    let languageCode = document.querySelector('meta[name="language-code"]').content;
    let fallbackLanguageCode = document.querySelector('meta[name="fallback-language-code"]').content;
    let ratingTarget = document.querySelector('.app-rating-list');
    let ratingTemplate = document.getElementById('app-rating-template');
    let ratingTemplateNoComments = document.getElementById('app-rating-template-no-comments');

    function load_comments(languageCode) {
        // note to myself: the code below checks if the fallback lang
        // is present in the language dropdown
        let langCode = global.id('comment_display_language_code');
        let fallback = Array.from(langCode.options)
            .filter((o) => o.value === fallbackLanguageCode);
        if (fallback.length !== 0) {
            fallbackLanguageCode = undefined;
        }
        fetchRatings(ratingUrl, languageCode, fallbackLanguageCode)
            .then((result) => {
                const ratings = result.ratings;
                const ratingLang = result.lang;
                ratingTarget.classList.remove('loading');
                ratingTarget.innerHTML = '';
                if (ratings.length > 0) {
                    ratings.forEach((rating) => {
                        const result = renderRating(ratingTemplate, rating, ratingLang);
                        ratingTarget.appendChild(result);
                        langCode.value = ratingLang;
                    });
                } else {
                    const result = renderEmptyRatings(ratingTemplateNoComments);
                    ratingTarget.appendChild(result);
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

    // language selection for posting
    function load_language(lang) {
        const commentTextarea = global.id('id_comment');
        commentTextarea.readOnly = true;
        fetchRatings(ratingUrl + "?current_user=true&lang=" + lang, lang)
            .then((result) => {
                let value = '';
                let ratings = result.ratings;
                if (ratings.length > 0) {
                    value = ratings[0].comment;
                }
                commentTextarea.value = value;
                commentTextarea.readOnly = false;
            }).catch(() => commentTextarea.readOnly = false);
    }

    global.id('id_language_code').addEventListener('change', (event) => {
        load_language(event.target.value);
    });

    // create markdown for app description
    let descriptionUrl = document.querySelector('meta[name="nextcloudappstore-app-description-url"]').content;
    let descriptionTarget = document.querySelector('.app-description');

    fetchDescription(descriptionUrl)
        .then(() => descriptionTarget.classList.remove('loading'));

    const langCode = global.id('comment_display_language_code');
    langCode.addEventListener('change', (event) => {
        load_comments(event.target.value);
    });

    load_comments(languageCode, true);
}(this));
