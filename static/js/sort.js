function updateSortIndicator(sortBy, direction) {
    var label = document.getElementById('sort-indicator');
    if (label) {
        var text = 'Sorted by: <strong>' + sortBy + '</strong> (' + direction + ')';
        label.innerHTML = text;
    }
}

function toggleSortDirection() {
    var dir = document.getElementById('sort-direction');
    var form = document.getElementById('sort-form');
    if (dir && form) {
        dir.value = dir.value === 'asc' ? 'desc' : 'asc';
        form.submit();
    }
}

function setSortBy(value) {
    var sortByInput = document.getElementById('sort-by-input');
    var form = document.getElementById('sort-form');
    if (sortByInput && form) {
        sortByInput.value = value;
        form.submit();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var sortByVal = document.getElementById('sort-by-val');
    var sortDirVal = document.getElementById('sort-dir-val');
    if (sortByVal && sortDirVal) {
        updateSortIndicator(sortByVal.value, sortDirVal.value);
    }

    document.querySelectorAll('.sort-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            setSortBy(this.dataset.sort);
        });
    });
});
