function newItem() {
    return {
        'itemName': $("#new-item").val(),
        'quantity': $("#quantity").val(),
    }
}

function clickedItem(x) {
    var itemRow = x.children;
    return {
        'itemName': itemRow[0].innerHTML,
        'quantity': itemRow[1].innerHTML
    } 
}

function getAdjacentRow(row) {
    var parentTable = $(row).closest('table')[0];
    var rowIndex = $(row).parent().index();

    var itemTable = $(parentTable).prev()[0];
    return item = $('#' + itemTable.id + ' tr').eq(rowIndex);
}

function clickedClose(x) {
    adjacentRow = getAdjacentRow(x);
    return {
        'itemName': adjacentRow[0].children[0].innerHTML,
        'quantity': adjacentRow[0].children[1].innerHTML,
    }  
}

function removeRow(x) {
    adjacentRow = getAdjacentRow(x);
    adjacentRow.remove();
}


// cross off item if clicked in click-area
$('#shopping-list').on('click', '.click-area', function (e) {
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
            $_this.toggleClass('found-item');
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
            $('#shopping-list tbody').append('<tr class="click-area"><td>'+ response.item + '</td><td>' + response.quantity + '</td><td>' + response.date_created + '</td></tr>');
            $('#close-buttons tbody').append('<tr><td class="close-button">✖</td></tr>');
        },
        error: function (data) {
            alert('this failed');
        }
    });
});

// remove list-item elements if close button is clicked
$('#close-buttons').on('click', '.close-button', function (e) {
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
            removeRow($_this);
            var r = 0;
            var rowIndex = $_this.parent().index();
            $_this.parent('tr').remove();
        },
        error: function (data) {
            alert('this failed');
        }
    });
});
