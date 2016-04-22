 var main = function(){
 // ------------------------------------------------------------------- //
 // вікно із списком коритсувачів
    $("#user_list_button").click(function(){
        $("#user_list").toggle("Puff");
    });

// ------------------------------------------------------------------- //
// ajax запит на відображення соуса поста
    $('img[name="edit_this_post"]').click(function(){   //.posts
        $('.flash').hide();
        var note_id = $(this).attr("id");

        // вихід при згортанні форми редагування
        var res = $('.posts').find('div[id="' + note_id + '"]').attr('style');
        if (res == 'display: block;') {
            $('.posts').find('div[id="' + note_id + '"]').toggle('blind');
            return;
            }

        $.ajax({
        type : 'GET',	   // тип запроса
        dataType : 'json', // тип загружаемых данных
        // timeout: 10,
        url  : '/ajax_view_note',    // URL по которому должен обрабатываться запрос, см. @app.route('/ajax_view_note'
        data : {           // передаваемые данные
            note_id
               },
        // в случае успешной передачи, выполняем функцию success иначе error
        success: function(data) {
            if (data.status == 'OK') {
                $('.posts').find('div[id="' + note_id + '"]').toggle('blind');
                $("div[id=" + note_id + "]").find("#blog_text_source").text(data.note_text);
                $("div[id=" + note_id + "]").find("#visible_post_source").attr('checked', data.visible_text);
                console.log("|AJAX|view|OK|сформовано запит|> ID:", note_id);
                }

            if (data.status == 'ERR') {
                // view error message
                $('.message_error').show();
                $('.message_error').text(data.message);
                console.log('|AJAX|view|ERROR|>', data.message);
                }

            },

        error: function (textStatus, errorThrown) {
            $('.message_error').show();
            $('.message_error').text('шось зовсім пішло не так :(((');
            console.log("|AJAX|view|ERROR|шось зовсім пішло не так :(((", errorThrown);
            }
        });
    });

// ------------------------------------------------------------------- //
// ajax change note
    $('input[name="submit_source"]').click(function() {
        $('.flash').hide();
        var submit_id = $(this).parent().attr("id");
        var note_text = $("div[id=" + submit_id + "]").find("#blog_text_source").val();
        var note_visible = $("div[id=" + submit_id + "]").find("#visible_post_source:checked").val();
        if (note_visible)
            {note_visible = 'True'}
        else
            {note_visible = 'False'}

        $.ajax({
            url: '/ajax_change_note',
//            timeout: 10,
            data : {
                    submit_id,
                    note_text,
                    note_visible
                    },
            type: 'POST',
            success: function(data) {
//                console.log('|AJAX|OK|змінено запис|', submit_id, data)
                if (data.status == 'OK') {
                    // відобреження зміни
                    $("table[id=" + submit_id + "]").find("pre").text(note_text)
                    if (note_visible == 'True')
                        {$("table[id=" + submit_id + "]").find(".visible").show();}
                    else
                        {$("table[id=" + submit_id + "]").find(".visible").hide();}
                    // сховати асинхронну форму редагування
                    $('.posts').find('div[id="' + submit_id + '"]').toggle('blind');

                    // view log
                    $('.message_ok').show();
                    $('.message_ok').text('запис успішно змінено');
                    console.log('|AJAX|change|OK|змінено запис|', submit_id);
                    }

                if (data.status == 'ERR') {
                    // view error message
                    $('.message_error').show();
                    $('.message_error').text(data.message);
                    console.log('|AJAX|change|ERROR|>', data.message);
                    }

            },
            error: function(error) {
                $('.message_error').show();
                $('.message_error').text('шось зовсім пішло не так :(((');
                console.log("|AJAX|change|ERROR|шось зовсім пішло не так :(((", errorThrown);
            }
        });

    })
}

// ------------------------------------------------------------------- //
$(document).ready(main);
