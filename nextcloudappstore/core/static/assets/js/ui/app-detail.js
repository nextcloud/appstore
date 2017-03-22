(function (global) {
    'use strict';
    let document = global.document;
    let ratingUrl = document.querySelector('meta[name="nextcloudappstore-app-ratings-url"]').content;
    let languageCode = document.querySelector('meta[name="language-code"]').content;
    let fallbackLanguageCode = document.querySelector('meta[name="fallback-language-code"]').content;
    let ratingTarget = document.querySelector('.app-rating-list');
    let ratingTemplate = document.getElementById('app-rating-template');
    let ratingTemplateNoComments = document.getElementById('app-rating-template-no-comments');
    let moment = global.moment;

    function load_comments(languageCode, initial=false) {
        fetch(ratingUrl)
            .then((response) => response.json())
            .then((ratings) => {
                ratingTarget.classList.remove('loading');
                ratingTarget.innerHTML = '';
                ratings = ratings
                    .filter(rating => rating.translations[languageCode] !== undefined)
                    .filter(rating => rating.translations[languageCode].comment !== undefined)
                    .filter(rating => rating.translations[languageCode].comment.trim() !== '');
                if (ratings.length > 0) {
                    ratings.forEach((rating) => {
                        let user = rating.user;
                        let fullName = user.firstName + " " + user.lastName;
                        if (fullName.trim() === '') {
                            fullName = 'Anonymous';
                        }
                        let comment = rating.translations[languageCode].comment;
                        let template = document.importNode(ratingTemplate.content, true);
                        template.childNodes[1].classList.add(createRatingClass(rating.rating));
                        let date = moment(rating.ratedAt);
                        template.querySelector('.date').innerHTML = date.locale(languageCode).fromNow();
                        template.querySelector('.author').innerHTML += global.escapeHtml(fullName.trim());
                        template.querySelector('.comment').innerHTML = renderMd(comment);
                        ratingTarget.appendChild(template);
                    });
                } else {
                    let langCode = global.id('comment_display_language_code');
                    let fallback = Array.from(langCode.options)
                        .filter((o) => o.value === fallbackLanguageCode);
                    if (initial && fallback.length > 0) {
                        load_comments(fallbackLanguageCode);
                        langCode.value = fallbackLanguageCode;
                    } else {
                        let templateNoComments = document.importNode(ratingTemplateNoComments.content, true);
                        ratingTarget.appendChild(templateNoComments);
                    }
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
        fetch(ratingUrl + "?current_user=true&lang=" + lang, {credentials: 'include'})
            .then((response) => response.json())
            .then((json) => {
                let value = '';
                if (json.length > 0 && json[0].translations[lang] !== undefined) {
                    value = json[0].translations[lang].comment;
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
    fetch(descriptionUrl).then((response) => response.text())
        .then((description) => {
            descriptionTarget.classList.remove('loading');
            descriptionTarget.innerHTML = renderMd(description);
        });

    const langCode = global.id('comment_display_language_code');
    langCode.addEventListener('change', (event) => {
        load_comments(event.target.value);
    });

    load_comments(languageCode, true);
}(this));
