// Invite
$(document).on('submit', '#invite', function (e) {
    $.ajax({
        type: 'POST',
        url: window.location.href,
        data: {
            email: $("#email-address").val(),
            requestType: 'invite',
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function (response) {
            alert(response.success);
        },
        error: function (response) {
            alert(response.responseJSON.error);
        },
    });
});