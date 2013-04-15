function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue =
                    decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function(){

    $("[rel='tooltip']").tooltip();
    
    $('.add-remove-journal').on('click', function(event) {
        var clicked = $(this);
        var verb = 'POST';
        if (!clicked.is(':checked')) {
            verb = 'DELETE';
        }
        var issn = clicked.attr('value');
        var data = {
            'issn': issn,
        };
        $.ajax({
            'type': verb,
            'url': '/poll/cart-item/',
            'data': JSON.stringify(data),
        });
    });


    $('.cart-item-up .cart-item.down .cart-item-top .cart-item-bottom').
        on('click', function(event) {
            event.preventDefault();
            var clicked = $(this);
            var href = clicked.attr('href');
            $('#cart-item-update').attr('action', href);
            $('#cart-item-update').submit();
        });

    $('.cart-item-delete').on('click', function(event) {
        event.preventDefault();
        var clicked = $(this);
        var href = clicked.attr('href');
        $('#cart-item-delete').attr('action', href);
        $('#cart-item-delete').submit();
    });
    
});
    
