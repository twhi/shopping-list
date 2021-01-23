class Dispatcher {
    constructor(delay, func) {
        this.delay = delay;
        this.func = func
        this.timerId = null;
    }

    run() {
        this.timerID = setTimeout(() => {
            this.func();
            this.run();
        }, this.delay);
    };

    stop() {
        window.clearTimeout(this.timerID);
    }

}

let getListContents = function () {
    var _data = {}
    $('#shopping-list tr').each(function(i, row) {
        if (row.dataset.pk) {
            _data[row.dataset.pk] = {
                'name': $(row).find('.item-name')[0].innerText,
                'quantity': $(row).find('.item-quantity')[0].innerText,
                'found': $(row).hasClass('found-item')
            }
        }
    });
    return _data
}

let updateTable = function(changes) {
    for (const [changeType, vals] of Object.entries(changes)) {
        if (Object.keys(vals).length > 0) {
            for (const [pk, values] of Object.entries(vals)) {
                if (changeType == 'updated') {
                    $(`tr[data-pk="${pk}"] td.item-name`).text(values.name);
                    $(`tr[data-pk="${pk}"] td.item-quantity`).text(values.quantity);
                    if (values.found) {
                        $(`tr[data-pk="${pk}"]`).addClass('found-item');
                    } else {
                        $(`tr[data-pk="${pk}"]`).removeClass('found-item');
                    }
                } else if (changeType == 'new') {
                    $('#shopping-list tr:last').after(values.html);
                } else if (changeType == 'removed') {
                    $(`tr[data-pk="${pk}"]`).remove();
                }
            }
        }
    }
}

let getData = function () {
    $.ajax({
        type: 'POST',
        url: window.location.href,
        data: {
            requestType: 'fetch',
            items: JSON.stringify(getListContents()),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function (data) {
            $("#list-area").html(data.shopping_list);
            updateTable(data.changes);
        },
        error: function (data) {
            fetch.stop();
        }
    });
}

const fetch = new Dispatcher(1000, getData);
fetch.run();
