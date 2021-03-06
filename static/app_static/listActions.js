// Helper functions start
function getNewItemParams() {
    return {
        'itemName': $("#new-item").val(),
        'quantity': $("#quantity").val(),
    }
}

function getRowValues(x) {
    var itemRow = $(x).closest('tr')[0].children;
    return {
        'itemName': itemRow[0].innerText.replace(/[\n\r]/g, ""),
        'quantity': itemRow[1].innerText.replace(/[\n\r]/g, ""),
        'timestamp': itemRow[4].innerText.replace(/[\n\r]/g, ""),
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
            $('#shopping-list tbody').append('<tr><td class="break-words"><div class="click-area">' + response.item + '</div></td><td class="break-words"><div class="click-area">' + response.quantity + '</div></td><td class="break-words hide-mobile"><small class="text-muted"><div class="click-area">' + response.date_created + '</div></small></td><td><div class="close-button">✖</div></td><td style="display:none;">' + response.timestamp + '</td></tr>');
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
        url: window.location.href  + '?' + $.param(getRowValues(this)),
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
            selected: JSON.stringify(getRowValues(this)),
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
// List actions end