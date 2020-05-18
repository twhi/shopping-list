function newItem() {
    return {
        'itemName': $("#new-item").val(),
        'quantity': $("#quantity").val(),
    }
}

function clickedItem(x) {
    var itemRow = $(x).closest('tr')[0].children;
    return {
        'itemName': itemRow[0].innerText,
        'quantity': itemRow[1].innerText,
        'timestamp': itemRow[4].innerText.trim(),
    } 
}

function getAdjacentRow(row) {
    var rowIndex = $(row).parent().index();
    return item = $('#shopping-list tr').eq(rowIndex);
}

function clickedClose(x) {
    adjacentRow = getAdjacentRow(x);
    return {
        'itemName': adjacentRow[0].children[0].innerText,
        'quantity': adjacentRow[0].children[1].innerText,
        'timestamp': adjacentRow[0].children[4].innerText.trim(),
    }  
}

function removeRow(x) {
    adjacentRow = getAdjacentRow(x);
    adjacentRow.remove();
}


// cross off item if clicked in click-area
$('body').on('click', '.click-area', function (e) {
    var $_this = $(this);
    $.ajax({
        type: 'POST',
        url: window.location.href,
        data: {
            requestType: 'found',
            selected: JSON.stringify(clickedItem(this)),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function (response) {
            var parentRow = $_this.closest('tr')[0] //.toggleClass('found-item');
            $(parentRow).toggleClass('found-item');
        },
        error: function (data) {
            alert('this failed');
        }
    });
});

// submit new item 
$(document).on('submit', '#post-form', function (e) {
    $.ajax({
        type: 'POST',
        url: window.location.href,
        data: {
            requestType: 'new',
            selected: JSON.stringify(newItem(this)),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function (response) {
            $('#shopping-list tbody').append('<tr><td style="word-break:break-all;"><div class="click-area">' + response.item + '</div></td><td style="word-break:break-all;"><div class="click-area">' + response.quantity + '</div></td><td><small class="text-muted"><div class="click-area">' + response.date_created + '</div></small></td><td class="close-button">✖</td><td style="display:none;">' + response.timestamp + '</td></tr>');
            // $('#close-buttons tbody').append('<tr><td class="close-button">✖</td></tr>');
        },
        error: function (data) {
            alert('this failed');
        }
    });
});

// remove list-item elements if close button is clicked
$('body').on('click', '.close-button', function (e) {
    var $_this = $(this);
    $.ajax({
        type: 'DELETE',
        url: window.location.href  + '?' + $.param(clickedClose(this)),
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name=csrfmiddlewaretoken]').val());
        },
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'delete'
        },
        success: function (response) {
            var rowIndex = $_this.parent().index();
            $_this.parent('tr').remove();
        },
        error: function (data) {
            alert('this failed');
        }
    });
});
