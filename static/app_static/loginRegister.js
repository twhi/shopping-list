// Log in
$(document).on('submit', '#login', function (e) {
    $("#login-btn").prop("disabled", true);
    $.ajax({
        type: 'POST',
        url: '',
        data: {
            username: $("#login-user").val(),
            password: $("#login-pass").val(),
            requestType: 'login',
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function (response) {
            if (response.redirect_url) {
                window.location.href = response.redirect_url;
                return
            }
        },
        error: function (data) {
            $("#login-error-message").text(data.responseJSON.error);
            $("#login-error-message").addClass("alert alert-danger");
            $("#login-btn").prop("disabled", false);
        },
    });
});

// Register
$(document).on('submit', '#registration', function (e) {
    $("#register-btn").prop("disabled", true);
    $.ajax({
        type: 'POST',
        url: '',
        data: {
            email: $("#reg-email").val(),
            first_name: $("#reg-first-name").val(),
            last_name: $("#reg-last-name").val(),
            password1: $("#reg-pass-1").val(),
            password2: $("#reg-pass-2").val(),
            requestType: 'registration',
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function (response) {
            if (response.redirect_url) {
                window.location.href = response.redirect_url;
                return
            }
        },
        error: function (data) {
            $("#reg-error-message").empty();
            for (e in data.responseJSON) {
                $("#reg-error-message").append(data.responseJSON[e][0].message, '<br>');
            }
            $("#reg-error-message").addClass("alert alert-danger");
            $("#register-btn").prop("disabled", false);
        },
    });
});