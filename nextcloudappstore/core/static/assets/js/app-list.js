(function () {
    'use strict';

    // reload page if featured checkbox is checked
    let form = document.getElementById('filter-form');
    form.querySelector('.auto-submit')
        .addEventListener('change', () => form.submit());

}(this));
