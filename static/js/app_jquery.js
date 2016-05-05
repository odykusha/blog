 var main = function(){
 // ------------------------------------------------------------------- //
 // вікно із списком користувачів
    $("#user_list_button").click(function(){
        $("#user_list").toggle("Puff");
    });

 // вікно авторизування кристувачів
    $("#auth_button").click(function(){
        $("#auth_form").toggle("Puff");
    });
 // ------------------------------------------------------------------- //
 // видалення запису
    // відобразити кнопку видалення
    $('.entries').on("click", 'img[name="delete_everything"]', function(){
        $(this).hide();
        $(this).next('span').show();
    });

    // сховати кнопку видалення
    $('.entries').on("click", 'abbr[name="delete_no"]', function() {
        $(this).parent().parent().find('img[name="delete_everything"]').show();
        $(this).parent().hide();
    });

 // видалення користувача
    // відобразити кнопку видалення
    $('.users').on("click", 'img[name="delete_everything"]', function(){
        $(this).hide();
        $(this).next('span').show();
    });

    // сховати кнопку видалення
    $('.users').on("click", 'abbr[name="delete_no"]', function() {
        $(this).parent().parent().find('img[name="delete_everything"]').show();
        $(this).parent().hide();
    });

// ------------------------------------------------------------------- //
// ajax запит на видалення користувача
    $('.users').on("click", 'abbr[name="delete_yes"]', function(){   //.posts
        var user_id = $(this).parent().attr("id");

        $.ajax({
        type : 'DELETE',	   // тип запросу
        dataType : 'json', // тип даних
        // timeout: 10,
        url  : '/ajax_delete_user',    // URL по запиту, див. @app.route('/ajax_delete_user'
        data : {           // дані які передаємо
            user_id
               },

        // якщо все ок, то виконуємо функцію success інакше error
        success: function(data) {
            if (data.status == 'OK') {
                $("tr[id=" + user_id + "]").hide();
                $('.message_ok').show('blind');
                $('.message_ok').text(data.message);
                console.log("|AJAX|delete_user|OK|видалено користувача, ID:", user_id);
                }

            if (data.status == 'ERR') {
                // відображаємо повідомлення з помилкою
                $('.message_error').show('blind');
                $('.message_error').text(data.message);
                console.log('|AJAX|delete_user|ERROR||', data.message);
                }

            },

        error: function (textStatus, errorThrown) {
            $('.message_error').show('blind');
            $('.message_error').text('шось зовсім пішло не так :(((');
            console.log("|AJAX|delete_user|ERROR|шось зовсім пішло не так :(((", errorThrown);
            }

        });
    });
// ------------------------------------------------------------------- //
// ajax запит на відображення соуса записа
    $('.entries').on("click", 'img[name="edit_this_post"]', function(){   //.posts
        var note_id = $(this).attr("id");

        // приховуємо дефолтне flash вікно
        var flash = $('.flash').attr('style');
        if (flash == 'display: block;') {
            $('.flash').hide('blind'); }
        var flash = $('.message_ok').attr('style');
        if (flash == 'display: block;') {
            $('.message_ok').hide('blind'); }
        var flash = $('.message_error').attr('style');
        if (flash == 'display: block;') {
            $('.message_error').hide('blind'); }

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
                console.log("|AJAX|view|OK|запит на запис, ID:", note_id);
                }

            if (data.status == 'ERR') {
                // відображаємо повідомлення з помилкою
                $('.message_error').show('blind');
                $('.message_error').text(data.message);
                console.log('|AJAX|view|ERROR||', data.message);
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
    $('.entries').on("click", 'input[name="submit_source"]', function() {
        var submit_id = $(this).parent().attr("id");
        var note_text = $("div[id=" + submit_id + "]").find("#blog_text_source").val();
        var note_visible = $("div[id=" + submit_id + "]").find("#visible_post_source:checked").val();
        if (note_visible)
            {note_visible = 'True'}
        else
            {note_visible = 'False'}

        // приховуємо дефолтне flash вікно
        var flash = $('.flash').attr('style');
        if (flash == 'display: block;') {
            $('.flash').hide('blind'); }
        var flash = $('.message_ok').attr('style');
        if (flash == 'display: block;') {
            $('.message_ok').hide('blind'); }
        var flash = $('.message_error').attr('style');
        if (flash == 'display: block;') {
            $('.message_error').hide('blind'); }


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
                    console.log('|AJAX|change|OK|змінено запис, ID:', submit_id);
                    }

                if (data.status == 'ERR') {
                    // відображаємо повідомлення з помилкою
                    $('.message_error').show('blind');
                    $('.message_error').text(data.message);
                    console.log('|AJAX|change|ERROR||', data.message);
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
    $('.entries').on("click", 'abbr[name="delete_yes"]', function() {
        var submit_id = $(this).parent().attr("id");

        // приховуємо дефолтне flash вікно
        var flash = $('.flash').attr('style');
        if (flash == 'display: block;') {
            $('.flash').hide('blind'); }
        var flash = $('.message_ok').attr('style');
        if (flash == 'display: block;') {
            $('.message_ok').hide('blind'); }
        var flash = $('.message_error').attr('style');
        if (flash == 'display: block;') {
            $('.message_error').hide('blind'); }


        $.ajax({
            url: '/ajax_delete_note',
            data: {
                submit_id
                },
            type: 'DELETE',
            success: function(data){
                if (data.status == 'OK') {
                    // скриваємо запис, який ми видалили
                    $("table[id='" + submit_id + "']").hide();

                    // показуємо повідомлення про успішність видалення запису
                    $('.message_ok').show('blind');
                    $('.message_ok').text(data.message);
                    console.log('|AJAX|delete|OK|видалено запис, ID:', submit_id);
                    }

                if (data.status == 'ERR') {
                    // відображаємо повідомлення з помилкою
                    $('.message_error').show('blind');
                    $('.message_error').text(data.message);
                    console.log('|AJAX|delete|ERROR||', data.message);
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
// ajax запит на створення запису
    $("input[name='submit']").click(function() {
        var note_text = $("textarea[name='blog_text']").val();
        var note_visible = $("input[name='visible_post']:checked").val();
        if (note_visible)
            {note_visible = 'True'}
        else
            {note_visible = 'False'}

        // приховуємо дефолтне flash вікно
        var flash = $('.flash').attr('style');
        if (flash == 'display: block;') {
            $('.flash').hide('blind'); }
        var flash = $('.message_ok').attr('style');
        if (flash == 'display: block;') {
            $('.message_ok').hide('blind'); }
        var flash = $('.message_error').attr('style');
        if (flash == 'display: block;') {
            $('.message_error').hide('blind'); }

        $.ajax({
            url: '/ajax_create_note',
            data: {
                note_text,
                note_visible
                },
            type: 'POST',
            success: function(data){
                if (data.status == 'OK') {
                    // відображаємо новий запис
                    // формуємо html код
                    // запихаємо його в початок

                    $('.entries').prepend(
    '<!-- тіло комента -->'+
    '<table class="post_head" id="'+ data.note_id +'">'+
        '<li>'+

           '<!-- видно всім -->'+
            '<tr>'+
                '<td class="left">'+
                    '<small>'+
                    '<div>'+
                        '<a class="not_like_link_id" href="/view/'+ data.note_id +'"> ІД: '+ data.note_id +'</a>'+
                    '</div>'+
                    '</small>'+
                '</td>'+
            '<td class="right">'+
                '<small>'+
                        '<div class="visible" style="display: none;">видно всім</div>'+
            '</small>'+
        '</td>'+
    '</tr>'+

'<!-- автор запису -->'+
            '<td class="left">'+
                '<h2 class="post">'+
                    '<a class="not_like_link_user" href="/users/'+ data.user_id + '"> '+ data.user_name +' </a>'+
                    '<!-- соус поста -->'+
                    '<img src="/static/img/edit.png" name="edit_this_post" id="'+ data.note_id +'" title="Редагувати"/>'+
                '</h2>'+
            '</td>'+

            '<td class="right">'+
                '<small>'+
                        data.timestamp +
                        ' <img src="/static/img/trash.png" name="delete_everything" id='+ data.note_id +' title="Видалити" />'+
                        '<span id="'+ data.note_id +'" name="delete_hide_form" style="display:none;">'+
                            '<abbr title="Видаляй" name="delete_yes">'+
                                '<img src="/static/img/accept.png"/>'+
                            '</abbr>'+
                            ' / '+
                            '<abbr title="Я передумав" name="delete_no">'+
                                '<img src="/static/img/cancel.png"/>'+
                            '</abbr>'+
                        '</span>'+

                '</small>'+
            '</td>'+
    '</table>'+

    '<!-- тіло комента -->'+
    '<table class="posts" id="'+ data.note_id +'">'+
        '<td>'+
            '<pre>'+ note_text +'</pre>'+
            '<div name="hidden_change_post" id="'+ data.note_id + '" class="hidden_post" role="form">'+
                '<input id="visible_post_source" name="visible_post_source" type="checkbox" value="y">відображати пост усім <br>'+
                '<textarea cols="70" id="blog_text_source" name="blog_text_source" placeholder="Текст напишіть тут. Можливе використання тегів" rows="7"></textarea><br>'+
                '<input id="submit_source" name="submit_source" type="submit" value="Змінити">'+
            '</div>'+
        '</td>'+
    '</table>');

                    // відображення visible текста
                    if (note_visible == 'True')
                        {$("table[id=" + data.note_id + "]").find(".visible").show();}
                    else
                        {$("table[id=" + data.note_id + "]").find(".visible").hide();}

                    // очищаємо форму ведення
                    $("textarea[name='blog_text']").val('');
                    if (note_visible == 'True') {
                        $("input[name='visible_post']").click(); }


                    // показуємо повідомлення про успішність видалення запису
                    $('.message_ok').show('blind');
                    $('.message_ok').text(data.message);
                    console.log('|AJAX|create|OK|створено запис, ID:', data.note_id);
                    }

                if (data.status == 'ERR') {
                    // відображаємо повідомлення з помилкою
                    $('.message_error').show('blind');
                    $('.message_error').text(data.message);
                    console.log('|AJAX|create|ERROR||', data.message);
                    }
                },

            error: function(error) {
                $('.message_error').show('blind');
                $('.message_error').text('шось зовсім пішло не так :(((');
                console.log("|AJAX|create|ERROR|шось зовсім пішло не так :(((", errorThrown);
                }
        });
    });

// ------------------------------------------------------------------- //
}

// ------------------------------------------------------------------- //
$(document).ready(main);
