(function worker() {
    $.ajax({
        url: window.location.href + '/fetch_list/',
        success: function(data) {
            $("#list-area").html(data.shopping_list);
        },
        complete: function() {
            setTimeout(worker.bind(null), 500000);
        }
    });
})();