// Helper functions start
function getNewItemParams() {
    return {
        'itemName': $("#new-item").val(),
        'quantity': $("#quantity").val(),
    }
}

function getRowPK(x) {
    return {
        'pk': $(x).closest('tr')[0].dataset.pk
    } 
}

function getUpdatedInfo(x) {
    var parentRow = $(x).closest('tr')[0];
    return {
        'pk': parentRow.dataset.pk,
        'name': $(parentRow).find('input').eq(0).val(),
        'quantity': $(parentRow).find('input').eq(1).val(),
    }
}
// Helper functions end

// List Actions start
// New Item
$(document).on('submit', '#post-form', function (e) {
    $.ajax({
        type: 'POST',
        url: window.location.href,
        data: {
            requestType: 'new',
            selected: JSON.stringify(getNewItemParams(this)),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function (response) {
            $('#shopping-list tbody').append(response.new_item);
            $('#new-item').val('');
            $('#quantity').val('');
            $('#new-item').focus();
        },
        error: function (data) {
            if (data.responseText) {
                alert(JSON.parse(data.responseText).message);
            } else {
                alert('Adding item failed. Uncaught error.');
            }
        }
    });
});

// Remove Item
$('body').on('click', '.close-button', function (e) {
    var _this = $(this);
    $.ajax({
        type: 'DELETE',
        url: window.location.href  + '?' + $.param(getRowPK(this)),
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name=csrfmiddlewaretoken]').val());
        },
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'delete'
        },
        success: function (response) {
            $(_this).closest('tr')[0].remove();
        },
        error: function (data) {
            alert('this failed');
        }
    });
});

// Found Item
$('body').on('click', '.click-area', function (e) {
    var $_this = $(this);
    $.ajax({
        type: 'POST',
        url: window.location.href,
        data: {
            requestType: 'found',
            selected: JSON.stringify(getRowPK(this)),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function (response) {
            var parentRow = $_this.closest('tr')[0];
            $(parentRow).toggleClass('found-item');
        },
        error: function (data) {
            alert('this failed');
        }
    });
});

// Edit Item
// display edit form
$('body').on('click', '.edit-button', function (e) {
    
    fetch.stop();

    var parentRow = $(this).closest('tr')[0];
    var name_input = $('<td class="click-area break-words"><input class="form-control edit-name"></td>');
    $(name_input).find('input').val($(parentRow).children(':eq(0)').text());
    $(parentRow).children(':eq(0)').replaceWith(name_input);

    var quantity_input = $('<td class="click-area break-words"><input class="form-control edit-quantity"></td>')
    $(quantity_input).find('input').val($(parentRow).children(':eq(1)').text());
    $(parentRow).children(':eq(1)').replaceWith(quantity_input);

    var button = $('<td><input class="update-item" type="submit" value="Update"></td>')
    $(parentRow).children(':eq(2)').replaceWith(button);

});
// send update to server
$('body').on('click', 'input.update-item', function (e) {
    var $_this = $(this);
    $.ajax({
        type: 'POST',
        url: window.location.href,
        data: {
            requestType: 'update',
            updated_fields: JSON.stringify(getUpdatedInfo(this)),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function (response) {
            var parentRow = $_this.closest('tr')[0];
            $(parentRow).replaceWith(response.html);
            fetch.run();
        },
        error: function (data) {
            if (data.responseText) {
                alert(JSON.parse(data.responseText).message);
            } else {
                alert('Adding item failed. Uncaught error.');
            }
        }
    });
});
// List actions end