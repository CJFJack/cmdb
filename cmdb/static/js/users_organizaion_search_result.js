$(document).ready(function () {
    table = $('#mytable').DataTable({
        responsive: true,
        language: {
            "url": "/static/js/i18n/Chinese.json"
        },
        ordering: false
    });
});
