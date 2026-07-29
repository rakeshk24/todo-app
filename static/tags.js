/**
 * tags.js — Makes tag checkbox lists searchable.
 * For each .tag-search-input, finds the associated .tag-checkboxes
 * container and filters visible checkboxes as the user types.
 */
(function () {
    function initTagSearch(searchInput, checkboxContainer) {
        searchInput.addEventListener('input', function () {
            var query = searchInput.value.toLowerCase().trim();
            var labels = checkboxContainer.querySelectorAll('.tag-checkbox-label');
            labels.forEach(function (label) {
                var name = label.getAttribute('data-tag-name') || '';
                label.style.display = name.indexOf(query) !== -1 ? '' : 'none';
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        // Add-todo form
        var addSearch = document.getElementById('tag-search-add');
        var addContainer = document.getElementById('tag-checkboxes-add');
        if (addSearch && addContainer) {
            initTagSearch(addSearch, addContainer);
        }

        // Edit-todo form
        var editSearch = document.getElementById('tag-search-edit');
        var editContainer = document.getElementById('tag-checkboxes-edit');
        if (editSearch && editContainer) {
            initTagSearch(editSearch, editContainer);
        }
    });
}());
