document.getElementById('copy-link').addEventListener('click', function () {
    var link = window.location.href;
    navigator.clipboard.writeText(link);
    document.getElementById('copy-status').innerHTML = 'Copied: ' + link;
});
