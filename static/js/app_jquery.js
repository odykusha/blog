 var main = function(){
    // вікно із списком коритсувачів
    $("#user_list_button").click(function(){
        $("#user_list").toggle("Puff");
    });

    // ajax запит на відображення соуса поста
    $('img[name="edit_this_post"]').click(function(){   //.posts
        var note_id = $(this).attr("id");
        $('.posts').find('div[id="' + note_id + '"]').toggle('blind');

        $.ajax({
        type : 'GET',	   // тип запроса
        dataType : 'json', // тип загружаемых данных
        url  : '/ajax_notes',    // URL по которому должен обрабатываться запрос, см. @app.route('/ajax'...
        data : {           // передаваемые данные
            note_id
               },
        // в случае успешной передачи, выполняем функцию success иначе error
        success: function(data) {
            $("div[id=" + note_id + "]").find("#blog_text_source").text(data.note_text);
            $("div[id=" + note_id + "]").find("#visible_post_source").attr('checked', data.visible_text);
            console.log("|OK|AJAX|успішно сформований запит|>", note_id, data);
            },

        error: function (textStatus, errorThrown) {
            console.log("|ERR|AJAX|не можливо сформувати запит|>", errorThrown);
            }
        });
    });

}

$(document).ready(main);
