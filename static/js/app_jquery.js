 var main = function(){
 // ------------------------------------------------------------------- //
 // вікно із списком коритсувачів
    $("#user_list_button").click(function(){
        $("#user_list").toggle("Puff");
    });

// ------------------------------------------------------------------- //
// ajax запит на відображення соуса записа
    $('img[name="edit_this_post"]').click(function(){   //.posts
        var note_id = $(this).attr("id");

        // приховуємо дефолтне flash вікно
        var flash = $('.flash').attr('style');
        if (flash == 'display: block;') {
            $('.flash').hide('blind'); }

        // вихід при згортанні форми редагування, щоб не відправляти дубляж ajax запиту
        var res = $('.posts').find('div[id="' + note_id + '"]').attr('style');
        if (res == 'display: block;') {
            $('.posts').find('div[id="' + note_id + '"]').toggle('blind');
            return;
            }

        $.ajax({
        type : 'GET',	   // тип запросу
        dataType : 'json', // тип даних
        // timeout: 10,
        url  : '/ajax_view_note',    // URL по запиту, див. @app.route('/ajax_view_note'
        data : {           // дані які передаємо
            note_id
               },

        // якщо все ок, то виконуємо функцію success інакше error
        success: function(data) {
            if (data.status == 'OK') {
                $('.hidden_post').hide();
                $('.posts').find('div[id="' + note_id + '"]').toggle('blind');
                $("div[id=" + note_id + "]").find("#blog_text_source").text(data.note_text);
                $("div[id=" + note_id + "]").find("#visible_post_source").attr('checked', data.visible_text);
                console.log("|AJAX|view|OK|сформовано запит| ID:", note_id);
                }

            if (data.status == 'ERR') {
                // відображаємо повідомлення з помилкою
                $('.message_error').show('blind');
                $('.message_error').text(data.message);
                console.log('|AJAX|view|ERROR|>', data.message);
                }

            },

        error: function (textStatus, errorThrown) {
            $('.message_error').show('blind');
            $('.message_error').text('шось зовсім пішло не так :(((');
            console.log("|AJAX|view|ERROR|шось зовсім пішло не так :(((", errorThrown);
            }
        });
    });

// ------------------------------------------------------------------- //
// ajax запит на зміну запису
    $('input[name="submit_source"]').click(function() {
        var submit_id = $(this).parent().attr("id");
        var note_text = $("div[id=" + submit_id + "]").find("#blog_text_source").val();
        var note_visible = $("div[id=" + submit_id + "]").find("#visible_post_source:checked").val();
        if (note_visible)
            {note_visible = 'True'}
        else
            {note_visible = 'False'}

//        // приховуємо дефолтне flash вікно
//        var flash = $('.flash').attr('style');
//        if (flash == 'display: block;') {
//            $('.flash').hide('blind'); }


        $.ajax({
            url: '/ajax_change_note',
            // timeout: 10,
            data : {
                    submit_id,
                    note_text,
                    note_visible
                    },
            type: 'POST',
            success: function(data) {
                if (data.status == 'OK') {

                    // водночас відобраежуємо виконані зміни
                    $("table[id=" + submit_id + "]").find("pre").text(note_text)
                    if (note_visible == 'True')
                        {$("table[id=" + submit_id + "]").find(".visible").show();}
                    else
                        {$("table[id=" + submit_id + "]").find(".visible").hide();}

                    // ховаємо асинхронну форму редагування
                    $('.posts').find('div[id="' + submit_id + '"]').toggle('blind');

                    // показуємо повідомлення про успішність виконання зміни
                    $('.message_ok').show('blind');
                    $('.message_ok').text(data.message);
                    console.log('|AJAX|change|OK|змінено запис|', submit_id);
                    }

                if (data.status == 'ERR') {
                    // відображаємо повідомлення з помилкою
                    $('.message_error').show('blind');
                    $('.message_error').text(data.message);
                    console.log('|AJAX|change|ERROR|>', data.message);
                    }
                },

            error: function(error) {
                $('.message_error').show('blind');
                $('.message_error').text('шось зовсім пішло не так :(((');
                console.log("|AJAX|change|ERROR|шось зовсім пішло не так :(((", errorThrown);
                }
        });
    });

// ------------------------------------------------------------------- //
// ajax видалення запису
    $("a[name='delete_note']").click(function() {
        var submit_id = $(this).parent().attr("id");

        // приховуємо дефолтне flash вікно
        var flash = $('.flash').attr('style');
        if (flash == 'display: block;') {
            $('.flash').hide('blind'); }

        $.ajax({
            url: '/ajax_delete_note',
            data: {
                submit_id
                },
            type: 'POST',
            success: function(data){
                if (data.status == 'OK') {
                    // скриваємо запис, який ми видалили
                    $("table[id='" + submit_id + "']").hide();

                    // показуємо повідомлення про успішність видалення запису
                    $('.message_ok').show('blind');
                    $('.message_ok').text(data.message);
                    console.log('|AJAX|delete|OK|запис видалено|', submit_id);
                    }

                if (data.status == 'ERR') {
                    // відображаємо повідомлення з помилкою
                    $('.message_error').show('blind');
                    $('.message_error').text(data.message);
                    console.log('|AJAX|delete|ERROR|>', data.message);
                    }
                },

            error: function(error) {
                $('.message_error').show('blind');
                $('.message_error').text('шось зовсім пішло не так :(((');
                console.log("|AJAX|delete|ERROR|шось зовсім пішло не так :(((", errorThrown);
                }

        });

    });


// ------------------------------------------------------------------- //

}

// ------------------------------------------------------------------- //
$(document).ready(main);
