function submitFilterForm() {
    document.getElementById("filter-form").submit();
}
var filterFormAutoInputs =
    Array.from(document.querySelectorAll("#filter-form input.auto-submit"));
filterFormAutoInputs.forEach(addEventListener('change', submitFilterForm));
