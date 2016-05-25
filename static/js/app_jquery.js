 var main = function(){
// ------------------------------------------------------------------- //
// ініціалізація чекбоксів
$('<input name="change_role" type="checkbox" checked>').replaceAll('div[id="1"]')
$('<input name="change_role" type="checkbox">').replaceAll('div[id="0"]')
//

// ------------------------------------------------------------------- //
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
// AJAX зміна прав користувача
    $('input[name="change_role"]').click(function() {
        var user_id = $(this).parent().parent().attr("id");
        // значення чекбокса статуса
        if($('tr[id="' + user_id + '"]').find('td[name="status"]').find('input').is(':checked')) {
            active_status_checked = 1; }
        else {
            active_status_checked = 0; }
        // значення чекбокса адмін ролі
        if($('tr[id="' + user_id + '"]').find('td[name="is_admin"]').find('input').is(':checked')) {
            admin_status_checked = 1;  }
        else {
            admin_status_checked = 0;  }

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
        type : 'POST',	   // тип запросу
        dataType : 'json', // тип даних
        // timeout: 10,
        url  : '/ajax_change_user',    // URL по запиту, див. @app.route('/ajax_change_user'
        data : {           // дані які передаємо
            user_id,
            active_status_checked,
            admin_status_checked
               },

        // якщо все ок, то виконуємо функцію success інакше error
        success: function(data) {
            if (data.status == 'OK') {
                $('.message_ok').show('blind');
                $('.message_ok').text(data.message);
                console.log("|AJAX|change_user|OK|змінено права користувачу, ID:", user_id);
                console.log("->|active_status is:", active_status_checked, '|admin_status is:', admin_status_checked);
                }

            if (data.status == 'ERR') {
                // відображаємо повідомлення з помилкою
                $('.message_error').show('blind');
                $('.message_error').text(data.message);
                console.log('|AJAX|change_user|ERROR||', data.message);
                }
            },

        error: function (textStatus, errorThrown) {
            $('.message_error').show('blind');
            $('.message_error').text('шось зовсім пішло не так :(((');
            console.log("|AJAX|change_user|ERROR|шось зовсім пішло не так :(((", errorThrown);
            }

        });
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
                    // запихаємо його в початок
                    $('.entries').prepend(data.created_html_block);

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