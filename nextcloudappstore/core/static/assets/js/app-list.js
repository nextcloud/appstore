(function (window) {
    'use strict';

    // reload page if featured checkbox is checked
    let form = window.document.getElementById('filter-form');
    let inputs = Array.from(form.querySelectorAll('.auto-submit'));
    inputs.forEach((input) => {
        input.addEventListener('change', () => form.submit());
    });

}(this));
