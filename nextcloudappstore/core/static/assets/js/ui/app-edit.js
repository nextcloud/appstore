(function (global) {
    'use strict';

    // App ownership transfer form
    let ownerTransferForm = document.getElementById('app-ownership-transfer-form');
    let appId = ownerTransferForm.getAttribute('data-app-id');
    let promptMsg = ownerTransferForm.getAttribute('data-prompt');
    let failMsg = ownerTransferForm.getAttribute('data-fail');
    ownerTransferForm.addEventListener('submit', (event) => {
        event.preventDefault();
        let appIdInput = window.prompt(promptMsg);
        if (appIdInput === appId) {
            ownerTransferForm.submit();
        } else {
            alert(failMsg);
        }
    });

}(this));
